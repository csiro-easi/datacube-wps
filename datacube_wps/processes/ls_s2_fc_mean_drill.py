import altair
import datetime as dt
from math import ceil
import numpy as np
import pandas as pd
import xarray as xr
from pywps import ComplexInput, ComplexOutput, LiteralInput, LiteralOutput

from .custom_input import AnyValueInput
from . import FORMATS, GeoDrill, chart_dimensions, log_call


class LS_S2_FC_Mean_Drill(GeoDrill):
    """
    Landsat/Sentinel-2 Fractional Cover Mean Drill. Works for both Points and Polygons.

    Values are means of polygon measurements or point values.
    """

    SHORT_NAMES = [
        "BS",
        "PV",
        "NPV",
        "TC"
    ]

    LONG_NAMES = [
        "Bare Soil",
        "Photosynthetic Vegetation",
        "Non-Photosynthetic Vegetation",
        "Total Cover"
    ]

    # This is when Landsat/Sentinel-2 data becomes available.
    DEFAULT_START_DATE = dt.datetime(2016, 1, 1, 0, 0, 0)

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
            ComplexInput(
                "start", "Start Date", supported_formats=[FORMATS["datetime"]], default=self.DEFAULT_START_DATE
            ),
            ComplexInput(
                "end", "End Date", supported_formats=[FORMATS["datetime"]]
            ),
        ]

    def output_formats(self):
        return [
            #LiteralOutput('image', 'Fractional Cover Drill Preview'),
            #LiteralOutput('url', 'Fractional Cover Drill Graph'),
            ComplexOutput('timeseries', 'Fractional Cover Drill Timeseries', supported_formats=[FORMATS['output_json']])
        ]

    @log_call
    def process_data(self, data: xr.Dataset, parameters: dict) -> pd.DataFrame:

        # 1. Convert no-data values to NaNs
        # 2. Take the mean of the non-NaN values
        # 3. Replace any NaN means with zero
        # 4. Round to 2-decimal places
        mean_ds = data.where(data != self.NO_DATA_VALUE, other=np.nan).mean(skipna=True, dim=["x", "y"]).fillna(0.0).round(2)

        # Build Total Cover means from PV and NPV.
        mean_ds["tc"] = mean_ds["pv"] + mean_ds["npv"]

        # Compute results.
        mean_ds = mean_ds.compute()

        # Rename band names from DC to suit WPS response code.
        mean_ds = mean_ds.rename({
            "bs" : "BS",
            "pv" : "PV",
            "npv" : "NPV",
            "tc" : "TC"
        })

        # Convert result to a DataFrame and return.
        df = mean_ds.to_dataframe()
        df = df.drop("spatial_ref", axis=1)
        df.reset_index(inplace=True)

        return df

    def render_chart(self, df: pd.DataFrame) -> altair.Chart:

        MONTHS_IN_YEAR = 12
        QUARTERS_IN_YEAR = 4

        n_time_ticks = ceil(df.shape[0] / MONTHS_IN_YEAR) * QUARTERS_IN_YEAR

        width, height = chart_dimensions(self.style)

        melted = df.melt("time", var_name="Cover Type", value_name="Percentage")
        melted = melted.dropna()

        style = self.style["table"]["columns"]

        chart = altair.Chart(melted,
                             width=width,
                             height=height,
                             title="Mean of Region - Fractional Cover")
        chart = chart.mark_line()
        chart = chart.encode(x=altair.X("time:T", axis=altair.Axis(title="Date", format="%b, %Y", tickCount=n_time_ticks)),
                             y=altair.Y("Percentage:Q", axis=altair.Axis(title="%")),
                             color=altair.Color("Cover Type:N",
                                                scale=altair.Scale(domain=self.SHORT_NAMES,
                                                                   range=[style[name]["chartLineColor"]
                                                                          for name in self.LONG_NAMES])),
                             tooltip=[altair.Tooltip(field="time", format="%b, %Y", title="Date", type="temporal"),
                                      "Percentage:Q",
                                      "Cover Type:N"])

        return chart

    def render_outputs(self, df, chart, is_enabled=True, name="Timeseries", header=True) -> dict:
        return super().render_outputs(df, chart, is_enabled=True, name=name, header=self.LONG_NAMES)