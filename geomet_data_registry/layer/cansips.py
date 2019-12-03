###############################################################################
#
# Copyright (C) 2019 Louis-Philippe Rousseau-Lambert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import logging
import os
from parse import parse
import re

from geomet_data_registry.layer.base import BaseLayer

LOGGER = logging.getLogger(__name__)


class CansipsLayer(BaseLayer):
    """CanSIPS layer"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.layer.cansips.CansipsLayer`  # noqa
        """

        provider_def = {'name': 'cansips'}

        BaseLayer.__init__(self, provider_def)

    def identify(self, filepath):
        """
        Identifies a file of the layer

        :param filepath: filepath from AMQP

        :returns: `list` of file properties
        """

        super().identify(filepath)

        self.model = 'cansips'

        LOGGER.debug('Loading model information from store')
        file_dict = json.loads(self.store.get_key(self.model))

        filename_pattern = file_dict[self.model]['filename_pattern']

        tmp = parse(filename_pattern, os.path.basename(filepath))

        file_pattern_info = {
            'wx_variable': '{}_{}_{}'.format(tmp.named['wx_variable'],
                                             tmp.named['pressure'],
                                             tmp.named['pres_value']),
            'year_': tmp.named['YYYY'],
            'month_': tmp.named['MM']
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        if self.wx_variable not in file_dict[self.model]['variable']:
            msg = 'Variable "{}" not in ' \
                  'configuration file'.format(self.wx_variable)
            LOGGER.warning(msg)
            return False

        weather_var = file_dict[self.model]['variable'][self.wx_variable]

        date_format = '%Y%m'
        date_ = '{}{}'.format(file_pattern_info['year_'],
                              file_pattern_info['month_'])
        reference_datetime = datetime.strptime(date_, date_format)
        self.model_run = '{}Z'.format(reference_datetime.strftime('%H'))

        begin, end, interval = weather_var['forecast_hours'].split('/')
        interval = int(re.sub("[^0-9]", "", interval))

        for band in file_dict[self.model]['bands']:

            dict_bands = file_dict[self.model]['bands']

            fhi = dict_bands[band]['forecast_interval']
            fhi = re.sub('[^0-9]', '', fhi)

            forecast_hour_datetime = reference_datetime + \
                relativedelta(months=int(fhi))

            member = dict_bands[band]['member']

            mem_str = str(member).zfill(2)
            layer_name = weather_var['geomet_layer'].format(mem_str)
            elevation = weather_var['elevation']
            time_format = '%Y-%m-%dT%H:%M:%SZ'
            str_mr = re.sub('[^0-9]',
                            '',
                            reference_datetime.strftime(time_format))
            str_fh = re.sub('[^0-9]',
                            '',
                            forecast_hour_datetime.strftime(time_format))
            identifier = '{}-{}-{}'.format(layer_name, str_mr, str_fh)
            expected_count = 1

            vrt = '''
<VRTDataset rasterXSize="145" rasterYSize="73">
    <SRS>'+proj=longlat +a=6371229 +b=6371229 +no_defs +pm=-359.88'</SRS>
    <GeoTransform> 178.75,  2.5000000000000000e+00,  0.0000000000000000e+00,
  9.1250000000000000e+01,  0.0000000000000000e+00,
 -2.5000000000000000e+00</GeoTransform>
        <VRTRasterBand dataType="Float64" band="1">
            <ComplexSource>
                <SourceFilename>{}</SourceFilename>
                <SourceBand>{}</SourceBand>
            </ComplexSource>
        </VRTRasterBand>
    </VRTDataset>'''.format(filepath, band).replace('\n', '')

            feature_dict = {
                'layer_name': layer_name,
                'filepath': vrt,
                'identifier': identifier,
                'reference_datetime': reference_datetime.strftime(time_format),
                'forecast_hour_datetime': forecast_hour_datetime.strftime(time_format), # noqa
                'member': member,
                'model': self.model,
                'elevation': elevation,
                'expected_count': expected_count
            }

            self.items.append(feature_dict)

        return True

    def add_time_key(self):
        """
        Add time keys when applicable:
            - model run default time
            - model run extent
            - forecast hour extent
        and for observation:
            - latest time step
        """

        # TODO add function to create time keys
        pass

    def __repr__(self):
        return '<ModelCanSIPSLayer> {}'.format(self.name)
