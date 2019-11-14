###############################################################################
#
# Copyright (C) 2019 Louis-Philippe Rousseau-Lambert
# Copyright (C) 2019 Etienne Pelletier
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

from datetime import datetime, timedelta
import json
import logging
import os
from parse import parse
import re

from geomet_data_registry.layer.base import BaseLayer

LOGGER = logging.getLogger(__name__)


class RepsLayer(BaseLayer):
    """REPS layer"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.layer.reps.REPSLayer`  # noqa
        """

        provider_def = {'name': 'reps'}
        self.type = None
        self.bands = None

        BaseLayer.__init__(self, provider_def)

    def identify(self, filepath):
        """
        Identifies a file of the layer

        :param filepath: filepath from AMQP

        :returns: `list` of file properties
        """

        self.filepath = filepath
        self.file_creation_datetime = datetime.fromtimestamp(
            os.path.getmtime(filepath)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.model = 'reps'

        LOGGER.debug('Loading model information from store')
        file_dict = json.loads(self.store.get_key(self.model))

        if self.filepath.endswith('allmbrs.grib2'):
            filename_pattern = file_dict[self.model]['member']['filename_pattern']  # noqa
            self.type = 'member'
        elif self.filepath.endswith('all-products.grib2'):
            filename_pattern = file_dict[self.model]['product']['filename_pattern']  # noqa
            self.type = 'product'

        tmp = parse(filename_pattern, os.path.basename(filepath))

        file_pattern_info = {
            'wx_variable': tmp.named['wx_variable'],
            'time_': tmp.named['YYYYMMDD_model_run'],
            'fh': tmp.named['forecast_hour']
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        var_path = file_dict[self.model][self.type]['variable']
        if self.wx_variable not in var_path:
            msg = 'Variable "{}" not in ' \
                  'configuration file'.format(self.wx_variable)
            LOGGER.warning(msg)
            return False

        weather_var = file_dict[self.model][self.type]['variable'][self.wx_variable]  # noqa

        time_format = '%Y%m%d%H'
        date_ = datetime.strptime(file_pattern_info['time_'], time_format)
        reference_datetime = date_
        self.model_run = '{}Z'.format(date_.strftime('%H'))
        forecast_hour_datetime = date_ + \
            timedelta(hours=int(file_pattern_info['fh']))

        if self.type == 'member':
            self.bands = file_dict[self.model]['member']['bands']
        elif self.type == 'product':
            self.bands = weather_var['bands']

        for band in self.bands.keys():
            vrt = '''\
<VRTDataset rasterXSize="145" rasterYSize="73">
    <SRS>'+proj=stere +lat_0=90 +lat_ts=60 +lon_0=250 +k=90 +x_0=0 +y_0=0 +a=6371229 +b=6371229 +units=m +no_defs'</SRS>
    <GeoTransform> -4.4174117578025218e+06,  1.5000000000000000e+04,  0.0000000000000000e+00,  4.5777534875770006e+05,  0.0000000000000000e+00, -1.5000000000000000e+04</GeoTransform>
    <VRTRasterBand dataType="Float64" band="1">
        <ComplexSource>
            <SourceFilename>{}</SourceFilename>
            <SourceBand>{}</SourceBand>
        </ComplexSource>
    </VRTRasterBand>
</VRTDataset>'''.format(self.filepath, band).replace('\n', '')  # noqa

            elevation = weather_var['elevation']
            time_format = '%Y-%m-%dT%H:%M:%SZ'
            str_mr = re.sub('[^0-9]',
                            '',
                            reference_datetime.strftime(time_format))
            str_fh = re.sub('[^0-9]',
                            '',
                            forecast_hour_datetime.strftime(time_format))

            expected_count = file_dict[self.model][self.type]['variable'][self.wx_variable]['model_run'][self.model_run]['files_expected']  # noqa

            for layer in weather_var['geomet_layers'].keys():

                if self.type == 'member':
                    member = self.bands[band]['member']
                    layer_name = layer.format(self.bands[band]['member'])

                elif self.type == 'product':
                    member = None
                    layer_name = layer.format(self.bands[band]['product'])

                identifier = '{}-{}-{}'.format(layer_name, str_mr, str_fh)

                feature_dict = {
                    'layer_name': layer_name,
                    'filepath': vrt,
                    'identifier': identifier,
                    'reference_datetime': reference_datetime.strftime(time_format), # noqa
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
        return '<ModelREPSLayer> {}'.format(self.name)
