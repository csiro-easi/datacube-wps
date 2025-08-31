import altair
import datetime as dt
from math import ceil
import numpy as np
import xarray as xr
from pywps import ComplexInput, ComplexOutput, LiteralInput, LiteralOutput

from . import FORMATS, PolygonDrill, PixelDrill, chart_dimensions, log_call, AnyValueInput
from pywps.inout.literaltypes import AnyValue # TEST

import dask
import dask.delayed
import time


class Trial_Drill(PolygonDrill):
    """
    Trial Drill. Attempt to simulate inputs/outputs of GSKY WPS endpoint to see how TerriaJS renders it.
    """

    SHORT_NAMES = ['BS', 'PV', 'NPV', 'NO_OBS']
    LONG_NAMES = ['Bare Soil',
                  'Photosynthetic Vegetation',
                  'Non-Photosynthetic Vegetation',
                  'Unobservable']

    DEFAULT_START_DATE = dt.datetime(2016, 1, 1, 0, 0, 0)

    def input_formats(self):
        return [
            AnyValueInput("geometry_id", "Point/Polygon Name", data_type="", allowed_values = AnyValue(), min_occurs=0),
            #LiteralInput(
            #    "geometry_id", "Point/Polygon Name", data_type="", allowed_values = AnyValue()
            #),
            #LiteralInput(
            #    "geometry_id", "Polygon Name", data_type="string", default=""
            #),
            #ComplexInput(
            #    "geometry", "Geometry", supported_formats=[FORMATS["polygon"],FORMATS["point"]]
            #),
            ComplexInput(
                "geometry", "Geometry", supported_formats=[FORMATS["geojson"]]
            ),
            ComplexInput(
                "start", "Start Date", supported_formats=[FORMATS["datetime"]], default=self.DEFAULT_START_DATE
            ),
            ComplexInput(
                "end", "End date", supported_formats=[FORMATS["datetime"]]
            ),
        ]

    def output_formats(self):
        return [
            #LiteralOutput('image', 'Fractional Cover Polygon Drill Preview'),
            #LiteralOutput('url', 'Fractional Cover Polygon Drill Graph'),
            ComplexOutput('timeseries', 'Test Drill Timeseries', supported_formats=[FORMATS['output_json']])
        ]

    # *****

    @log_call
    def process_data(self, data, parameters): # returns pandas.DataFrame

        new_ds = xr.Dataset(
            {
                'BS': ('time', np.zeros(len(data.time))),
                'PV': ('time', np.zeros(len(data.time))),
                'NPV': ('time', np.zeros(len(data.time))),
                'NO_OBS': ('time', np.zeros(len(data.time)))
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

    def render_outputs(self, df, chart, is_enabled=True, name="Timeseries", header=True):
        return super().render_outputs(df, chart, is_enabled=True, name=name, header=self.LONG_NAMES)