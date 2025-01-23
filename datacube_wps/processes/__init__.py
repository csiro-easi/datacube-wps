import io
import json
import os
from functools import wraps
from timeit import default_timer
from collections import Counter

import altair
import boto3
import botocore
import datacube
import numpy as np
import pandas
import pyarrow as pa
import pyarrow.parquet as pq
import pywps.configuration as config
import rasterio.features
import xarray
from botocore.client import Config
from dask.distributed import Client
from datacube.utils.geometry import CRS, Geometry
from datacube.utils.rio import configure_s3_access
from datacube.virtual.impl import Product, Juxtapose
from dateutil.parser import parse
from pywps import ComplexInput, ComplexOutput, Format, Process
from pywps.app.exceptions import ProcessError


FORMATS = {
    # Defines the format for the returned object
    # in this case a JSON object containing a CSV
    "output_json": Format(
        "application/vnd.terriajs.catalog-member+json",
        schema="https://tools.ietf.org/html/rfc7159",
        encoding="utf-8",
    ),
    "point": Format(
        "application/vnd.geo+json", schema="http://geojson.org/geojson-spec.html#point"
    ),
    "polygon": Format(
        "application/vnd.geo+json",
        schema="http://geojson.org/geojson-spec.html#polygon",
    ),
    "datetime": Format(
        "application/vnd.geo+json", schema="http://www.w3.org/TR/xmlschema-2/#dateTime"
    ),
}

GB = 1.0e9
MAX_BYTES_IN_GB = 20.0
MAX_BYTES_PER_OBS_IN_GB = 2.0


def log_call(func):
    @wraps(func)
    def log_wrapper(*args, **kwargs):
        name = func.__name__
        for index, arg in enumerate(args):
            try:
                arg_name = func.__code__.co_varnames[index]
            except (AttributeError, KeyError, IndexError):
                arg_name = f"arg #{index}"
            print(f"{name} {arg_name}: {arg}")
        for key, value in kwargs.items():
            print(f"{name} {key}: {value}")

        start = default_timer()
        result = func(*args, **kwargs)
        end = default_timer()
        print("{} returned {}".format(name, result))
        print("{} took {:.3f}s".format(name, end - start))
        return result

    return log_wrapper


@log_call
def _uploadToS3(filename, data, mimetype):
    session = boto3.Session(profile_name="default")
    bucket = config.get_config_value("s3", "bucket")
    s3 = session.client("s3")
    s3.upload_fileobj(
        data,
        bucket,
        filename,
        ExtraArgs={"ACL": "public-read", "ContentType": mimetype},
    )

    # Create unsigned s3 client for determining public s3 url
    s3 = session.client("s3", config=Config(signature_version=botocore.UNSIGNED))
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        ExpiresIn=0,
        Params={"Bucket": bucket, "Key": filename},
    )


def upload_chart_html_to_S3(chart: altair.Chart, process_id: str):
    html_io = io.StringIO()
    chart.save(html_io, format="html")#, engine="vl-convert")
    html_bytes = io.BytesIO(html_io.getvalue().encode())
    return _uploadToS3(process_id + "/chart.html", html_bytes, "text/html")


def upload_chart_svg_to_S3(chart: altair.Chart, process_id: str):
    img_io = io.StringIO()
    chart.save(img_io, format="svg")#, engine="vl-convert")
    img_bytes = io.BytesIO(img_io.getvalue().encode())
    return _uploadToS3(process_id + "/chart.svg", img_bytes, "image/svg+xml")


def write_df_to_parquet(df: pandas.DataFrame, process_id: str, identifier: str):
    table = pa.Table.from_pandas(df)
    writer = pa.BufferOutputStream()
    pq.write_table(table, writer, compression="snappy")
    body = bytes(writer.getvalue())

    bucket = config.get_config_value("s3", "bucket")
    key = "/".join([identifier, process_id, process_id]) + ".snappy.parquet"
    session = boto3.Session()
    dev_s3_client = session.client("s3")
    dev_s3_client.put_object(Body=body, Bucket=bucket, Key=key)
    return f"s3://{bucket}/{key}"


# from https://stackoverflow.com/a/16353080
class DatetimeEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return super(DatetimeEncoder, o).default(o)
        except TypeError:
            return str(o)


def geometry_mask(geom, geobox, all_touched=False, invert=False):
    return rasterio.features.geometry_mask(
        [geom.to_crs(geobox.crs)],
        out_shape=geobox.shape,
        transform=geobox.affine,
        all_touched=all_touched,
        invert=invert,
    )


def mostcommon_crs(datasets: list):
    """Adapted from https://github.com/GeoscienceAustralia/dea-notebooks/blob/develop/Tools/dea_tools/datahandling.py"""
    crs_list = [str(i.crs) for i in datasets]
    crs_mostcommon = None
    if len(crs_list) > 0:
        # Identify most common CRS
        crs_counts = Counter(crs_list)
        crs_mostcommon = crs_counts.most_common(1)[0][0]
    else:
        raise ProcessError('No common CRS was found for the product query')
    return crs_mostcommon


def wofls_fuser(dest, src):
    where_nodata = (src & 1) == 0
    np.copyto(dest, src, where=where_nodata)
    return dest


def chart_dimensions(style):
    if "chart" in style and "width" in style["chart"]:
        width = style["chart"]["width"]
    else:
        width = 1000
    if "height" in style and "height" in style["chart"]:
        height = style["chart"]["height"]
    else:
        height = 300

    return (width, height)


def _guard_rail(input, box):
    measurement_dicts = input.output_measurements(box.product_definitions)

    byte_count = 1
    for x in box.shape:
        byte_count *= x
    byte_count *= sum(np.dtype(m.dtype).itemsize for m in measurement_dicts.values())

    if byte_count > MAX_BYTES_IN_GB * GB:
        raise ProcessError(
            ("requested area requires {}GB data to load - " "maximum is {}GB").format(
                int(byte_count / GB), MAX_BYTES_IN_GB
            )
        )

    grouped = box.box

    assert len(grouped.shape) == 1

    if grouped.shape[0] == 0:
        raise ProcessError("no data returned for query")

    bytes_per_obs = byte_count / grouped.shape[0]
    if bytes_per_obs > MAX_BYTES_PER_OBS_IN_GB * GB:
        raise ProcessError(
            (
                "requested time slices each requires {}GB data to load - "
                "maximum is {}GB"
            ).format(int(bytes_per_obs / GB), MAX_BYTES_PER_OBS_IN_GB)
        )


def _datetimeExtractor(data):
    return parse(json.loads(data)["properties"]["timestamp"]["date-time"])


def _parse_geom(request_json):
    features = request_json["features"]
    if len(features) < 1:
        # can't drill if there is no geometry
        raise ProcessError("no features specified")

    if len(features) > 1:
        # do we need multipolygon support here?
        raise ProcessError("multiple features specified")

    feature = features[0]

    if hasattr(request_json, "crs"):
        crs = CRS(request_json["crs"]["properties"]["name"])
    elif hasattr(feature, "crs"):
        crs = CRS(feature["crs"]["properties"]["name"])
    else:
        # http://geojson.org/geojson-spec.html#coordinate-reference-system-objects
        crs = CRS("urn:ogc:def:crs:OGC:1.3:CRS84")

    return Geometry(feature["geometry"], crs)


def _get_feature(request):
    stream = request.inputs["geometry"][0].stream
    request_json = json.loads(stream.readline())

    return _parse_geom(request_json)


def _get_time(request):
    if "start" not in request.inputs or "end" not in request.inputs:
        return None

    def _datetimeExtractor(data):
        return parse(json.loads(data)["properties"]["timestamp"]["date-time"])

    return (
        _datetimeExtractor(request.inputs["start"][0].data),
        _datetimeExtractor(request.inputs["end"][0].data),
    )


def _get_parameters(request):
    if "parameters" not in request.inputs:
        return {}

    stream = request.inputs["parameters"][0].stream
    params = json.loads(stream.readline())

    return params


def _render_outputs(
    uuid,
    style,
    df: pandas.DataFrame,
    chart,
    json_version,
    is_enabled=True,
    name="Timeseries",
    header=True,
):
    if chart:
        html_url = upload_chart_html_to_S3(chart, str(uuid))
        img_url = upload_chart_svg_to_S3(chart, str(uuid))

    try:
        csv_df = df.drop(columns=["latitude", "longitude"])
    except KeyError:
        csv_df = df

    csv_df.set_index("time", inplace=True)
    csv = csv_df.to_csv(header=header, date_format="%Y-%m-%d")

    if "table" in style:
        table_style = {"tableStyle": style["table"]}
    else:
        table_style = {}

    # Terria v7 API
    if json_version == "v7":
        output_dict = {
            "data": csv,
            "isEnabled": is_enabled,
            "type": "csv",
            "name": name,
            **table_style,
        }
    # Terria v8 API
    elif json_version == "v8":
        columns = [column for column in style["table"]["columns"]]
        units = [style["table"]["columns"][column]["units"] for column in columns]
        colours = [style["table"]["columns"][column]["chartLineColor"] for column in columns]

        output_dict = {
            "type": "csv",
            "name": name,
            "csvString": csv,
            "columns": [
                {
                    "name": column,
                    "units": unit
                } for column, unit in zip(columns,units)
            ],
            "defaultStyle": {
                "hidden": False,
                "chart": {
                    "lines": [
                        {
                            "isSelectedInWorkbench": True,
                            "yAxisColumn": column,
                            "color": colour
                        } for column, colour in zip(columns, colours)
                    ]
                }
            }
        }
    
    else:
        raise ValueError("No Terria JSON version specified")
    output_json = json.dumps(output_dict, cls=DatetimeEncoder)

    if chart:
        outputs = {
            "image": {"data": img_url},
            "url": {"data": html_url},
            "timeseries": {"data": output_json},
            # "output_format": {"data": "application/vnd.terriajs.catalog-member.json"},
        }

    else:
        outputs = {
            "timeseries": {"data": output_json},
            # "output_format": {"data": "application/vnd.terriajs.catalog-member.json"},
        }

    return outputs


def _populate_response(response, outputs):
    for ident, output_value in outputs.items():
        if ident in response.outputs:
            if "data" in output_value:
                response.outputs[ident].data = output_value["data"]
            if "output_format" in output_value:
                response.outputs[ident].output_format = output_value["output_format"]
            if "url" in output_value:
                response.outputs[ident].url = output_value["url"]
            if "timeseries" in output_value:
                response.outputs[ident].timeseries = output_value["timeseries"]


def num_workers():
    return int(os.getenv("DATACUBE_WPS_NUM_WORKERS", "4"))


class PixelDrill(Process):
    def __init__(self, about, input, style):
        if "geometry_type" in about:
            assert about["geometry_type"] == "point"

        super().__init__(
            handler=self.request_handler,
            inputs=self.input_formats(),
            outputs=self.output_formats(),
            **{
                key: value
                for key, value in about.items()
                if key not in ["geometry_type", "guard_rail"]
            },
        )

        self.about = about
        self.input = input
        self.style = style
        self.json_version = "v8"

    def input_formats(self):
        return [
            ComplexInput(
                "geometry", "Location (Lon, Lat)", supported_formats=[FORMATS["point"]]
            ),
            ComplexInput(
                "start", "Start Date", supported_formats=[FORMATS["datetime"]]
            ),
            ComplexInput("end", "End date", supported_formats=[FORMATS["datetime"]]),
        ]

    def output_formats(self):
        return [
            ComplexOutput(
                "timeseries",
                "Timeseries Drill",
                supported_formats=[FORMATS["output_json"]],
            )
        ]

    def request_handler(self, request, response):
        time = _get_time(request)
        feature = _get_feature(request)
        parameters = _get_parameters(request)

        result = self.query_handler(time, feature, parameters=parameters)

        if 'csv' in self.style:
            outputs = self.render_outputs(result["data"], None)
        elif 'table' in self.style:
            outputs = self.render_outputs(result["data"], result["chart"])
        else:
            raise ProcessError('No output style configured for process!')

        _populate_response(response, outputs)
        return response

    @log_call
    def query_handler(self, time, feature, dask_client=None, parameters=None):
        if parameters is None:
            parameters = {}

        if dask_client is None:
            dask_client = Client(
                n_workers=1, processes=False, threads_per_worker=num_workers()
            )

        with dask_client:
            configure_s3_access(
                aws_unsigned=False,
                region_name=os.getenv("AWS_DEFAULT_REGION", "auto"),
                client=dask_client,
            )

            with datacube.Datacube() as dc:
                data = self.input_data(dc, time, feature)

        df = self.process_data(data, {"time": time, "feature": feature, **parameters})

        # If csv specified, return timeseries in csv form
        if 'csv' in self.style:
            return {"data": df}
        # If table style specified in config, return chart (static timeseries)
        elif 'table' in self.style:
            chart = self.render_chart(df)
            return {"data": df, "chart": chart}
        else:
            return {}

    @log_call
    def input_data(self, dc, time, feature):
        if time is None:
            bag = self.input.query(dc, geopolygon=feature)
        else:
            bag = self.input.query(dc, time=time, geopolygon=feature)

        # X: Try using this code from polygon drill input_data func instead
        output_crs = self.input.get('output_crs')
        resolution = self.input.get('resolution')
        align = self.input.get('align')

        if not (output_crs and resolution):
            if type(self.input) in (Product,):
                if not bag.product_definitions[self.input._product].grid_spec:
                    output_crs = mostcommon_crs(list(bag.bag))
            elif type(self.input) in (Juxtapose,):
                grid_specs = [product_definition.grid_spec for product_definition in list(bag.product_definitions.values()) if getattr(product_definition, 'grid_spec', None)]
                if len(set(grid_specs)) > 1:
                    raise ValueError('Multiple grid_spec detected across all products - override target output_crs, resolution in config')
                else:
                    if not resolution:
                        raise ValueError('add target resolution to config')
                    elif not output_crs:
                        output_crs = mostcommon_crs(bag.contained_datasets())                    

        box = self.input.group(bag, output_crs=output_crs, resolution=resolution, align=align)

        # X: Instead of this...
        
        # Get output_crs/resolution/align params if product grid_spec is not defined
        #if bag.product_definitions[self.input._product].grid_spec is None:
        #    output_crs = self.input.get('output_crs')
        #    resolution = self.input.get('resolution')
        #    align = self.input.get('align')
        #    if output_crs is None:
        #        output_crs = mostcommon_crs(list(bag.bag))
        #    box = self.input.group(bag, output_crs=output_crs, resolution=resolution, align=align)
        #else:
        #    box = self.input.group(bag)

        lonlat = feature.coords[0]
        measurements = self.input.output_measurements(bag.product_definitions)

        data = self.input.fetch(box, dask_chunks={"time": 1})
        data = data.compute()

        coords = {
            "longitude": np.array([lonlat[0]]),
            "latitude": np.array([lonlat[1]]),
            "time": data.time.data,
        }

        result = xarray.Dataset()
        for measurement_name, measurement in measurements.items():
            result[measurement_name] = xarray.DataArray(
                data[measurement_name],
                dims=("time", "longitude", "latitude"),
                coords=coords,
                attrs={
                    key: value
                    for key, value in measurement.items()
                    if key in ["flags_definition"]
                },
            )
        return result

    def process_data(self, data: xarray.Dataset, parameters: dict) -> pandas.DataFrame:
        raise NotImplementedError

    def render_chart(self, df: pandas.DataFrame) -> altair.Chart:
        raise NotImplementedError

    def render_outputs(
        self,
        df: pandas.DataFrame,
        chart: altair.Chart,
        is_enabled=True,
        name="Timeseries",
        header=True,
    ):
        return _render_outputs(
            self.uuid,
            self.style,
            df,
            chart,
            json_version=self.json_version,
            is_enabled=is_enabled,
            name=name,
            header=header,
        )


class PolygonDrill(Process):
    def __init__(self, about, input, style):
        if "geometry_type" in about:
            assert about["geometry_type"] == "polygon"

        super().__init__(
            handler=self.request_handler,
            inputs=self.input_formats(),
            outputs=self.output_formats(),
            **{
                key: value
                for key, value in about.items()
                if key not in ["geometry_type", "guard_rail"]
            },
        )

        self.about = about
        self.input = input
        self.style = style
        self.mask_all_touched = False
        self.json_version = "v8"

    def input_formats(self):
        return [
            ComplexInput(
                "geometry", "Geometry", supported_formats=[FORMATS["polygon"]]
            ),
            ComplexInput(
                "start", "Start Date", supported_formats=[FORMATS["datetime"]]
            ),
            ComplexInput("end", "End date", supported_formats=[FORMATS["datetime"]]),
        ]

    def output_formats(self):
        return [
            ComplexOutput(
                "timeseries",
                "Timeseries Drill",
                supported_formats=[FORMATS["output_json"]],
                as_reference=False,
            )
        ]

    def request_handler(self, request, response):

        time = _get_time(request)
        feature = _get_feature(request)
        parameters = _get_parameters(request)

        result = self.query_handler(time, feature, parameters=parameters)

        if 'csv' in self.style:
            outputs = self.render_outputs(result["data"], None)
        elif 'table' in self.style:
            outputs = self.render_outputs(result["data"], result["chart"])
        else:
            raise ProcessError('No output style configured for process!')

        _populate_response(response, outputs)
        return response

    @log_call
    def query_handler(self, time, feature, dask_client=None, parameters=None):
        if parameters is None:
            parameters = {}

        if dask_client is None:
            dask_client = Client(
                n_workers=num_workers(), processes=True, threads_per_worker=1
            )

        with dask_client:
            configure_s3_access(
                aws_unsigned=False,
                region_name=os.getenv("AWS_DEFAULT_REGION", "auto"),
                client=dask_client,
            )

            with datacube.Datacube() as dc:
                data = self.input_data(dc, time, feature)

        df = self.process_data(data, {"time": time, "feature": feature, **parameters})

        # If csv specified, return timeseries in csv form
        if 'csv' in self.style:
            return {"data": df}
        # If table style specified in config, return chart (static timeseries)
        elif 'table' in self.style:
            chart = self.render_chart(df)
            return {"data": df, "chart": chart}
        else:
            return {}

    def input_data(self, dc, time, feature):
        if time is None:
            bag = self.input.query(dc, geopolygon=feature)
        else:
            bag = self.input.query(dc, time=time, geopolygon=feature)
        output_crs = self.input.get('output_crs')
        resolution = self.input.get('resolution')
        align = self.input.get('align')

        if not (output_crs and resolution):
            if type(self.input) in (Product,):
                if not bag.product_definitions[self.input._product].grid_spec:
                    output_crs = mostcommon_crs(list(bag.bag))
            elif type(self.input) in (Juxtapose,):
                grid_specs = [product_definition.grid_spec for product_definition in list(bag.product_definitions.values()) if getattr(product_definition, 'grid_spec', None)]
                if len(set(grid_specs)) > 1:
                    raise ValueError('Multiple grid_spec detected across all products - override target output_crs, resolution in config')
                else:
                    if not resolution:
                        raise ValueError('add target resolution to config')
                    elif not output_crs:
                        output_crs = mostcommon_crs(bag.contained_datasets())                    

        box = self.input.group(bag, output_crs=output_crs, resolution=resolution, align=align)

        if self.about.get("guard_rail", True):
            # HACK: Get around issue where VirtualDatasetBox has a geobox but thinks it doesn't because load_natively flag is True.
            # Need load_natively to be False to be able to call box.shape() inside guard_rail check function.
            # Don't have time to understand how VirtualDatasets work and why this is happening in any more detail - just need the drill to work :)
            run_hack = box.load_natively and box.geobox is not None
            if run_hack:
                load_natively = box.load_natively
                box.load_natively = False
            _guard_rail(self.input, box)
            if run_hack:
                box.load_natively = load_natively

        # TODO customize the number of processes
        data = self.input.fetch(box, dask_chunks={"time": 1})
        mask = geometry_mask(
            feature, data.geobox, all_touched=self.mask_all_touched, invert=True
        )

        data = self.mask_polygon(data, mask)

        return data

    def mask_polygon(self, data: xarray.Dataset, mask) -> xarray.Dataset:
        # mask out data outside requested polygon
        for band_name, band_array in data.data_vars.items():
            if "nodata" in band_array.attrs:
                data[band_name] = band_array.where(
                    mask, other=band_array.attrs["nodata"]
                )
            else:
                data[band_name] = band_array.where(mask)
        return data

    def process_data(self, data: xarray.Dataset, parameters: dict) -> pandas.DataFrame:
        raise NotImplementedError

    def render_chart(self, df: pandas.DataFrame) -> altair.Chart:
        raise NotImplementedError

    def render_outputs(
        self,
        df: pandas.DataFrame,
        chart=None,
        is_enabled=True,
        name="Timeseries",
        header=True,
    ):
        # patch in here for the time being
        # might be better
        if "wit" == self.about.get("identifier", "").lower():
            url = write_df_to_parquet(
                df, str(self.uuid), self.about.get("identifier").lower()
            )
            return {'url': {'data': url}}
        return _render_outputs(
            self.uuid,
            self.style,
            df,
            chart,
            json_version=self.json_version,
            is_enabled=is_enabled,
            name=name,
            header=header,
        )
