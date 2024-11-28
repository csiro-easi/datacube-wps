import altair
from math import ceil
import numpy as np
import xarray as xr
from pywps import ComplexOutput, LiteralOutput

from . import FORMATS, PolygonDrill, chart_dimensions, log_call


class LS_S2_FC_Drill(PolygonDrill):
    SHORT_NAMES = ['TC']
    LONG_NAMES = ['Total Cover']

    def output_formats(self):
        return [
                #LiteralOutput('image', 'Fractional Cover Polygon Drill Preview'),
                #LiteralOutput('url', 'Fractional Cover Polygon Drill Graph'),
                ComplexOutput('timeseries', 'Fractional Cover Polygon Drill Timeseries', supported_formats=[FORMATS['output_json']])
        ]

    @log_call
    def process_data(self, data, parameters): # returns pandas.DataFrame

        NO_DATA = 255

        mask_da = data['tc'] != NO_DATA

        masked_da = data['tc'].where(mask_da)

        mean_da = masked_da.mean(dim=['x','y'], skipna=True).compute()

        df = mean_da.to_dataframe()
        df = df.drop('spatial_ref', axis=1)
        df.reset_index(inplace=True)

        return df

    def render_chart(self, df):

        MONTHS_IN_YEAR = 12
        QUARTERS_IN_YEAR = 4

        width, height = chart_dimensions(self.style)

        chart = altair.Chart(df,
                             width=width,
                             height=height,
                             title='Mean Percentage of Total Cover')

        chart = chart.mark_line()

        n_time_ticks = ceil(df.shape[0] / MONTHS_IN_YEAR) * QUARTERS_IN_YEAR

        try:
            line_colour = self.style['table']['columns']['Total Cover %']['chartLineColor']
        except KeyError:
            line_colour = '#3B7F00'

        chart = chart.encode(
            x=altair.X('time:T', axis=altair.Axis(title='Time', format='%b %Y', tickCount=n_time_ticks)),
            y=altair.Y('tc:Q', axis=altair.Axis(title='Mean TC%')),
            color=altair.ColorValue(line_colour)
        )

        return chart

    def render_outputs(self, df, chart):

        return super().render_outputs(df, chart, is_enabled=True, name='tc', header=self.LONG_NAMES)
