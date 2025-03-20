import altair
import datetime as dt
from math import ceil
import numpy as np
import pandas as pd
import xarray as xr
from pywps import ComplexInput, ComplexOutput, LiteralInput, LiteralOutput

from . import FORMATS, GeoDrill, chart_dimensions, log_call

from .custom_input import AnyValueInput


class LS_S2_FC_TC_Prop_Drill(GeoDrill):
    """
    Landsat/Sentinel-2 Fractional Cover Total Cover Proportion Drill.

    Values are proportion of polygon where total cover is within user defined range.
    """

    SHORT_NAMES = [
        "pixel_frac"
    ]

    LONG_NAMES = [
        "pixel frac" # Name to match GSKY MODIS equivilant
    ]

    # This is when Landsat/Sentinel-2 data becomes available.
    #DEFAULT_START_DATE = dt.datetime(2016, 1, 1, 0, 0, 0)

    # This is the no-data value for the area masked by the input polygon.
    POLYGON_MASK_VALUE = 254

    # This is the no-data value for the input product.
    NO_DATA_VALUE = 255

    def input_formats(self):
        return [
            AnyValueInput(
                "geometry_id", "Point/Polygon Name", min_occurs=0
            ),
            ComplexInput(
                "geometry", "Geometry", supported_formats=[FORMATS["geojson"]]
            ),
            AnyValueInput(
                "geoglam_clip_lower", "Total cover lower value", min_occurs=0
            ),
            AnyValueInput(
                "geoglam_clip_upper", "Total cover upper value", min_occurs=0
            ),
            #ComplexInput(
            #    "start", "Start Date", supported_formats=[FORMATS["datetime"]], default=self.DEFAULT_START_DATE
            #),
            #ComplexInput(
            #    "end", "End Date", supported_formats=[FORMATS["datetime"]]
            #),
        ]

    def output_formats(self):
        return [
            #LiteralOutput('image', 'Total Cover Proportion Drill Preview'),
            #LiteralOutput('url', 'Total Cover Proportion Drill Graph'),
            ComplexOutput('timeseries', 'Total Cover Proportion Drill Timeseries', supported_formats=[FORMATS['output_json']])
        ]

    # *****

    def mask_polygon(self, data: xr.Dataset, mask) -> xr.Dataset:
        """
        Overridden to mask the area around the selected polygon using a different value to default no_data value.
        This is required to be able to compute the no_data area seperately from the polygon mask area in the process_data func.
        """

        # mask out data outside requested polygon
        for band_name, band_array in data.data_vars.items():
            data[band_name] = band_array.where(
                mask, other=self.POLYGON_MASK_VALUE)
        return data
    
    @log_call
    def process_data(self, data: xr.Dataset, parameters: dict) -> pd.DataFrame:

        # Apply a lower limit, if not defined by user, use 0%
        lower_limit = 0.0
        if "geoglam_clip_lower" in parameters:
            try:
                lower_limit = float(parameters["geoglam_clip_lower"])
            except:
                pass # Use default lower limit if argument is not numeric.

        # Apply an upper limit, if not defined by user, use 100%
        upper_limit = 100.0
        if "geoglam_clip_upper" in parameters:
            try:
                upper_limit = float(parameters["geoglam_clip_upper"])
            except:
                pass # Use default upper limit if argument is not numeric.

        # Count of cells within polygon.
        total_count_ds = data.where(data != self.POLYGON_MASK_VALUE, other=np.nan).count(dim=["x", "y"])

        # Count of cells that fall within defined range. Polygon and NoData mask values are > 100 so are excluded automatically.
        range_count_ds = data.where(data >= lower_limit and data <= upper_limit, other=np.nan).count(dim=["x", "y"])

        # Compute percentage (count of cells within range / count of cells) * 100
        prop_ds = (range_count_ds / total_count_ds * 100.0).compute()

        # Change time values from mid-month to start-of-month.
        new_dates = []
        for t in prop_ds["time"].values:
            tmp_pt = pd.to_datetime(t)
            tmp_dt = dt.datetime(tmp_pt.year, tmp_pt.month, 1, 0, 0, 0)
            new_dates.append(np.datetime64(tmp_dt))
        prop_ds = prop_ds.assign_coords({"time": new_dates})

        # Rename dim from tc to pixel_frac.
        prop_ds = prop_ds.rename({
            "tc": "pixel_frac"
        })

        # Convert result to a DataFrame and return.
        df = prop_ds.to_dataframe()
        df = df.drop("spatial_ref", axis=1)
        df.reset_index(inplace=True)

        return df

    def render_chart(self, df: pd.DataFrame) -> altair.Chart:

        MONTHS_IN_YEAR = 12
        QUARTERS_IN_YEAR = 4

        width, height = chart_dimensions(self.style)

        chart = altair.Chart(df,
                             width=width,
                             height=height,
                             title='Proportion of Total Cover within range')

        chart = chart.mark_line()

        n_time_ticks = ceil(df.shape[0] / MONTHS_IN_YEAR) * QUARTERS_IN_YEAR

        try:
            line_colour = self.style['table']['columns']['pixel frac']['chartLineColor']
        except KeyError:
            line_colour = '#FFFFFF'

        chart = chart.encode(
            x=altair.X('time:T', axis=altair.Axis(title='Time', format='%b %Y', tickCount=n_time_ticks)),
            y=altair.Y('pixel_frac:Q', axis=altair.Axis(title='%')),
            color=altair.ColorValue(line_colour)
        )

        return chart

    def render_outputs(self, df, chart, is_enabled=True, name="Timeseries", header=True) -> dict:
        return super().render_outputs(df, chart, is_enabled=True, name=name, header=self.LONG_NAMES)