import altair
import datetime as dt
from math import ceil
import numpy as np
import xarray as xr
from pywps import ComplexInput, ComplexOutput, LiteralOutput

from . import FORMATS, PolygonDrill, PixelDrill, chart_dimensions, log_call


class LS_S2_FC_Drill(PolygonDrill):
    """
    Landsat/Sentinel-2 Fractional Cover Polygon Drill
    EASI Product: ls_s2_fc_c3

    For a given polygon, returns the bs, pv, npv and null percentage for each time.

    Whichever measurement (bs, pv or npv) has the highest value for a given cell determines what
    that cell is classified as. The output is the percentage of the polygon area that each cell
    has been classified as.
    """

    SHORT_NAMES = ['BS', 'PV', 'NPV', 'NO_OBS']
    LONG_NAMES = ['Bare Soil',
                  'Photosynthetic Vegetation',
                  'Non-Photosynthetic Vegetation',
                  'Unobservable']

    POLYGON_MASK_VALUE = 254
    NO_DATA_VALUE = 255

    DEFAULT_START_DATE = dt.datetime(2016, 1, 1, 0, 0, 0)

    def input_formats(self):
        return [
            ComplexInput(
                "geometry", "Geometry", supported_formats=[FORMATS["polygon"]]
            ),
            ComplexInput(
                "start", "Start Date", supported_formats=[FORMATS["datetime"]], default=self.DEFAULT_START_DATE
            ),
            ComplexInput("end", "End date", supported_formats=[FORMATS["datetime"]]),
        ]

    def output_formats(self):
        return [
            #LiteralOutput('image', 'Fractional Cover Polygon Drill Preview'),
            #LiteralOutput('url', 'Fractional Cover Polygon Drill Graph'),
            ComplexOutput('timeseries', 'Fractional Cover Polygon Drill Timeseries', supported_formats=[FORMATS['output_json']])
        ]

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
    def process_data(self, data, parameters): # returns pandas.DataFrame

        # Placeholder for results
        bs = np.empty(len(data.time), dtype=np.float32)
        pv = np.empty(len(data.time), dtype=np.float32)
        npv = np.empty(len(data.time), dtype=np.float32)
        no_obs = np.empty(len(data.time), dtype=np.float32)

        # Compute each time index one-by-one to avoid high memory usage
        for t in range(len(data.time)):

            # Compute the time index
            d = data.isel(time=t).compute()

            # Make polgon and no_data masks
            poly_mask = d == self.POLYGON_MASK_VALUE
            no_data_mask = d == self.NO_DATA_VALUE

            # Calculate the valid vs invalid pixel counts
            total = d.count(dim=['x', 'y'])
            total_valid = (d != self.NO_DATA_VALUE and d != self.POLYGON_MASK_VALUE).sum(dim=['x', 'y'])
            not_pixels = (d == self.NO_DATA_VALUE).sum(dim=['x', 'y'])

            # Combine both masks into one for the remainder of the calculations
            d = d.where(d != self.POLYGON_MASK_VALUE, other=self.NO_DATA_VALUE)
    
            maxFC = d.to_array(dim='variable', name='maxFC')

            # Set all no_data values to -1
            # This is because the mask/no_data values (254/255) are higher than valid values (0-100), which would cause issues in the next argmax call
            FC_int = maxFC.astype('int8')
            FC_int = FC_int.where(FC_int != self.NO_DATA_VALUE, other=-1)

            BSPVNPV = FC_int.argmax(dim='variable')

            FC_mask = (maxFC != self.NO_DATA_VALUE).all(dim='variable')

            BSPVNPV = BSPVNPV.where(FC_mask)

            FC_dominant = xr.Dataset({
                'bs': (BSPVNPV == 0).where(FC_mask),
                'pv': (BSPVNPV == 1).where(FC_mask),
                'npv': (BSPVNPV == 2).where(FC_mask)
            })

            FC_count = FC_dominant.sum(dim=['x', 'y'])

            # Fractional cover pixel count method
            # Get number of FC pixels, divide by total number of pixels per polygon
            bs[t] = (FC_count.bs / total_valid)['bs'] * 100
            pv[t] = (FC_count.pv / total_valid)['pv'] * 100
            npv[t] = (FC_count.npv / total_valid)['npv'] * 100
            no_obs[t] = (not_pixels / total_valid)['bs'] * 100

        new_ds = xr.Dataset(
            {
                'BS': ('time', bs),
                'PV': ('time', pv),
                'NPV': ('time', npv),
                'NO_OBS': ('time', no_obs)
            },
            coords = {
                'time':  data.time
            }
        )

        df = new_ds.to_dataframe()
        df = df.drop('spatial_ref', axis=1)
        df.reset_index(inplace=True)

        return df

    def render_chart(self, df):

        MONTHS_IN_YEAR = 12
        QUARTERS_IN_YEAR = 4

        n_time_ticks = ceil(df.shape[0] / MONTHS_IN_YEAR) * QUARTERS_IN_YEAR

        width, height = chart_dimensions(self.style)

        melted = df.melt('time', var_name='Cover Type', value_name='Area')
        melted = melted.dropna()

        style = self.style['table']['columns']

        chart = altair.Chart(melted,
                             width=width,
                             height=height,
                             title='Percentage of Area - Fractional Cover')
        chart = chart.mark_area()
        chart = chart.encode(x=altair.X('time:T', axis=altair.Axis(format='%b, %Y', tickCount=n_time_ticks)),
                             y=altair.Y('Area:Q', stack='normalize'),
                             color=altair.Color('Cover Type:N',
                                                scale=altair.Scale(domain=self.SHORT_NAMES,
                                                                   range=[style[name]['chartLineColor']
                                                                          for name in self.LONG_NAMES])),
                             tooltip=[altair.Tooltip(field='time', format='%b, %Y', title='Date', type='temporal'),
                                      'Area:Q',
                                      'Cover Type:N'])

        return chart

    def render_outputs(self, df, chart):
        return super().render_outputs(df, chart, is_enabled=True, name='FC', header=self.LONG_NAMES)


class LS_S2_FC_Point_Drill(PixelDrill):
    """
    Landsat/Sentinel-2 Fractional Cover Point Drill
    EASI Product: ls_s2_fc_c3

    For a given point, returns the bs, pv, npv and null percentage for each time.

    These are just the values read directly from the data.
    """

    SHORT_NAMES = ['BS', 'PV', 'NPV', 'NO_OBS']
    LONG_NAMES = ['Bare Soil',
                  'Photosynthetic Vegetation',
                  'Non-Photosynthetic Vegetation',
                  'Unobservable']

    NO_DATA_VALUE = 255

    DEFAULT_START_DATE = dt.datetime(2016, 1, 1, 0, 0, 0)

    def input_formats(self):
        return [
            ComplexInput(
                "geometry", "Location (Lon, Lat)", supported_formats=[FORMATS["point"]]
            ),
            ComplexInput(
                "start", "Start Date", supported_formats=[FORMATS["datetime"]], default=self.DEFAULT_START_DATE
            ),
            ComplexInput("end", "End date", supported_formats=[FORMATS["datetime"]]),
        ]

    def output_formats(self):
        return [
                #LiteralOutput('image', 'Fractional Cover Point Drill Preview'),
                #LiteralOutput('url', 'Fractional Cover Point Drill Graph'),
                ComplexOutput('timeseries', 'Fractional Cover Point Drill Timeseries', supported_formats=[FORMATS['output_json']])
        ]

    @log_call
    def process_data(self, data, parameters): # returns pandas.DataFrame

        data = data.compute()

        bs = np.empty(len(data.time), dtype=np.float32)
        pv = np.empty(len(data.time), dtype=np.float32)
        npv = np.empty(len(data.time), dtype=np.float32)
        no_obs = np.empty(len(data.time), dtype=np.float32)

        for t in range(len(data.time)):
            bs[t] = data['bs'][t,0,0]
            pv[t] = data['pv'][t,0,0]
            npv[t] = data['npv'][t,0,0]
            no_obs[t] = 0.0
            if bs[t] == self.NO_DATA_VALUE and pv[t] == self.NO_DATA_VALUE and npv[t] == self.NO_DATA_VALUE:
                bs[t] = 0.0
                pv[t] = 0.0
                npv[t] = 0.0
                no_obs[t] = 100.0

        new_ds = xr.Dataset(
            {
                'BS': ('time', bs),
                'PV': ('time', pv),
                'NPV': ('time', npv),
                'NO_OBS': ('time', no_obs)
            },
            coords = {
                'time':  data.time
            }
        )

        df = new_ds.to_dataframe()
        df = df.drop('spatial_ref', axis=1)
        df.reset_index(inplace=True)

        return df

    def render_chart(self, df):

        MONTHS_IN_YEAR = 12
        QUARTERS_IN_YEAR = 4

        n_time_ticks = ceil(df.shape[0] / MONTHS_IN_YEAR) * QUARTERS_IN_YEAR

        width, height = chart_dimensions(self.style)

        melted = df.melt('time', var_name='Cover Type', value_name='Point')
        melted = melted.dropna()

        style = self.style['table']['columns']

        chart = altair.Chart(melted,
                             width=width,
                             height=height,
                             title='Percentage at Point - Fractional Cover')
        chart = chart.mark_area()
        chart = chart.encode(x=altair.X('time:T', axis=altair.Axis(format='%b, %Y', tickCount=n_time_ticks)),
                             y=altair.Y('Point:Q', stack='normalize'),
                             color=altair.Color('Cover Type:N',
                                                scale=altair.Scale(domain=self.SHORT_NAMES,
                                                                   range=[style[name]['chartLineColor']
                                                                          for name in self.LONG_NAMES])),
                             tooltip=[altair.Tooltip(field='time', format='%b, %Y', title='Date', type='temporal'),
                                      'Point:Q',
                                      'Cover Type:N'])

        return chart

    def render_outputs(self, df, chart):
        return super().render_outputs(df, chart, is_enabled=True, name='FC', header=self.LONG_NAMES)
