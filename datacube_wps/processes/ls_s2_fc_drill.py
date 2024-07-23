import altair
import numpy as np
import xarray as xr
from pywps import ComplexOutput, LiteralOutput

from . import FORMATS, PolygonDrill, chart_dimensions, log_call, DatetimeEncoder


class LS_S2_FC_Drill(PolygonDrill):
    SHORT_NAMES = ['TC']
    LONG_NAMES = ['Total Cover']

    def output_formats(self):
        return [
                ComplexOutput('timeseries', 'Fractional Cover Polygon Drill Timeseries',
                              supported_formats=[FORMATS['output_json']])
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
        pass

    def render_outputs(self, df, chart):

        name = 'tc'

        try:
            csv_df = df.drop(columns=["latitude", "longitude"])
        except KeyError:
            csv_df = df

        csv_df.set_index("time", inplace=True)
        csv = csv_df.to_csv(header=self.LONG_NAMES, date_format="%Y-%m-%d")

        #if "table" in style:
        #    table_style = {"tableStyle": style["table"]}
        #else:
        table_style = {}

        output_dict = {
            "data": csv,
            "isEnabled": True,
            "type": "csv",
            "name": name,
            **table_style,
        }

        import json
        output_json = json.dumps(output_dict, cls=DatetimeEncoder)

        outputs = {
            #"image": {"data": img_url},
            #"url": {"data": html_url},
            "timeseries": {"data": output_json},
        }

        return outputs
        #pass
        #return super().render_outputs(df, chart, is_enabled=True, name="tc",
                                      #header=self.LONG_NAMES)
