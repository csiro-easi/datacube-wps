from timeit import default_timer

import altair
import numpy as np
import xarray
from datacube.utils.masking import make_mask
from pywps import ComplexOutput, LiteralOutput

from . import FORMATS, PolygonDrill, chart_dimensions, log_call


class LSFCDrill(PolygonDrill):
    SHORT_NAMES = ['BS', 'PV', 'NPV', 'Unobservable']
    LONG_NAMES = ['Bare Soil',
                  'Photosynthetic Vegetation',
                  'Non-Photosynthetic Vegetation',
                  'Unobservable']

    def output_formats(self):
        return [ComplexOutput('timeseries', 'Landsat Fractional Cover Polygon Drill Timeseries',
                              supported_formats=[FORMATS['output_json']])]

    @log_call
    def process_data(self, data, parameters):
        wofs_mask_flags = [
            dict(dry=True),
            dict(terrain_shadow=False, high_slope=False, cloud_shadow=False, cloud=False)
        ]

        total = data.count(dim=['x', 'y'])
        total_valid = (data != -1).sum(dim=['x', 'y'])

        # TODO enable this check, investigate why it fails
        # if total_valid <= 0:
        #     raise ProcessError('query returned no data')

        total_invalid = (np.isnan(data)).sum(dim=['x', 'y'])
        not_pixels = total_valid - (total - total_invalid)

        # following robbi's advice, cast the dataset to a dataarray
        maxFC = data.to_array(dim='variable', name='maxFC')

        # turn FC array into integer only as nanargmax doesn't seem to handle floats the way we want it to
        FC_int = maxFC.astype('int16')

        # use numpy.nanargmax to get the index of the maximum value along the variable dimension
        # BSPVNPV=np.nanargmax(FC_int, axis=0)
        BSPVNPV = FC_int.argmax(dim='variable')

        FC_mask = np.isfinite(maxFC).all(dim='variable')   # pylint: disable=no-member,unexpected-keyword-arg

        # #re-mask with nans to remove no-data
        BSPVNPV = BSPVNPV.where(FC_mask)

        FC_dominant = xarray.Dataset({
            'bs': (BSPVNPV == 0).where(FC_mask),
            'pv': (BSPVNPV == 1).where(FC_mask),
            'npv': (BSPVNPV == 2).where(FC_mask)
        })

        FC_count = FC_dominant.sum(dim=['x', 'y'])

        # Fractional cover pixel count method
        # Get number of FC pixels, divide by total number of pixels per polygon
        new_ds = xarray.Dataset({
            'bs': (FC_count.bs / total_valid)['bs'] * 100,
            'pv': (FC_count.pv / total_valid)['pv'] * 100,
            'npv': (FC_count.npv / total_valid)['npv'] * 100,
            'Unobservable': (not_pixels / total_valid)['bs'] * 100
        })

        new_ds = new_ds.compute()

        df = new_ds.to_dataframe()
        df = df.drop('spatial_ref', axis=1)
        df.reset_index(inplace=True)
        return df

    def render_chart(self, df):
        width, height = chart_dimensions(self.style)

        melted = df.melt('time', var_name='Cover Type', value_name='Area')
        melted = melted.dropna()

        style = self.style['table']['columns']

        chart = altair.Chart(melted,
                             width=width,
                             height=height,
                             title='Percentage of Area - Fractional Cover')
        chart = chart.mark_area()
        chart = chart.encode(x='time:T',
                             y=altair.Y('Area:Q', stack='normalize'),
                             color=altair.Color('Cover Type:N',
                                                scale=altair.Scale(domain=self.SHORT_NAMES,
                                                                   range=[style[name]['chartLineColor']
                                                                          for name in self.LONG_NAMES])),
                             tooltip=[altair.Tooltip(field='time', format='%d %B, %Y', title='Date', type='temporal'),
                                      'Area:Q',
                                      'Cover Type:N'])

        return chart

    def render_outputs(self, df, chart):
        return super().render_outputs(df, chart, is_enabled=True, name="LSFC",
                                      header=self.LONG_NAMES)
