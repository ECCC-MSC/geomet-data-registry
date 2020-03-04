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
from geomet_data_registry.util import DATE_FORMAT

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

        super().identify(filepath)

        self.model = 'reps'

        LOGGER.debug('Loading model information from store')
        self.file_dict = json.loads(self.store.get_key(self.model))

        if self.filepath.endswith('allmbrs.grib2'):
            filename_pattern = self.file_dict[self.model]['member']['filename_pattern']  # noqa
            self.type = 'member'
        elif self.filepath.endswith('all-products.grib2'):
            filename_pattern = self.file_dict[self.model]['product']['filename_pattern']  # noqa
            self.type = 'product'

        tmp = parse(filename_pattern, os.path.basename(filepath))

        file_pattern_info = {
            'wx_variable': tmp.named['wx_variable'],
            'time_': tmp.named['YYYYMMDD_model_run'],
            'fh': tmp.named['forecast_hour']
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        var_path = self.file_dict[self.model][self.type]['variable']
        if self.wx_variable not in var_path:
            msg = 'Variable "{}" not in ' \
                  'configuration file'.format(self.wx_variable)
            LOGGER.warning(msg)
            return False

        runs = self.file_dict[self.model][self.type]['variable'][self.wx_variable]['model_run'] # noqa
        self.model_run_list = list(runs.keys())

        weather_var = self.file_dict[self.model][self.type]['variable'][self.wx_variable]  # noqa
        self.geomet_layers = weather_var['geomet_layers']

        time_format = '%Y%m%d%H'
        self.date_ = datetime.strptime(file_pattern_info['time_'], time_format)
        reference_datetime = self.date_
        self.model_run = '{}Z'.format(self.date_.strftime('%H'))
        forecast_hour_datetime = self.date_ + \
            timedelta(hours=int(file_pattern_info['fh']))

        if self.type == 'member':
            self.bands = self.file_dict[self.model]['member']['bands']
        elif self.type == 'product':
            self.bands = weather_var['bands']

        for band in self.bands.keys():
            vrt = 'vrt://{}?bands={}'.format(self.filepath, band)  # noqa

            elevation = weather_var['elevation']
            str_mr = re.sub('[^0-9]',
                            '',
                            reference_datetime.strftime(DATE_FORMAT))
            str_fh = re.sub('[^0-9]',
                            '',
                            forecast_hour_datetime.strftime(DATE_FORMAT))

            expected_count = self.file_dict[self.model][self.type]['variable'][self.wx_variable]['model_run'][self.model_run]['files_expected']  # noqa

            for layer, layer_config in self.geomet_layers.items():
                if self.type == 'member':
                    member = self.bands[band]['member']
                    layer_name = layer.format(str(self.bands[band]['member']).zfill(2))  # noqa

                elif self.type == 'product':
                    member = None
                    layer_name = layer.format(str(self.bands[band]['product']).zfill(2))  # noqa

                identifier = '{}-{}-{}'.format(layer_name, str_mr, str_fh)

                forecast_hours = layer_config['forecast_hours']
                begin, end, interval = [int(re.sub('[^0-9]', '', value))
                                        for value in
                                        forecast_hours.split('/')]
                fh = int(file_pattern_info['fh'])

                feature_dict = {
                    'layer_name': layer_name,
                    'layer_name_unformatted': layer,
                    'filepath': vrt,
                    'identifier': identifier,
                    'reference_datetime': reference_datetime.strftime(DATE_FORMAT),  # noqa
                    'forecast_hour_datetime': forecast_hour_datetime.strftime(DATE_FORMAT),  # noqa
                    'member': member,
                    'model': self.model,
                    'elevation': elevation,
                    'expected_count': expected_count,
                    'forecast_hours': {
                        'begin': begin,
                        'end': end,
                        'interval': forecast_hours.split('/')[2]
                    },
                    'layer_config': layer_config,
                    'register_status': True,
                }

                if not self.is_valid_interval(fh, begin, end, interval):
                    feature_dict['register_status'] = False
                    LOGGER.debug('Forecast hour {} not included in {} as '
                                 'defined for layer {}. File will not be '
                                 'added to registry for this layer'
                                 .format(fh, forecast_hours, layer_name))

                self.items.append(feature_dict)

        return True

    def __repr__(self):
        return '<ModelREPSLayer> {}'.format(self.name)
