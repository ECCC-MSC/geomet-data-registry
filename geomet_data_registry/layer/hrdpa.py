###############################################################################
#
# Copyright (C) 2020 Etienne Pelletier
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
import re

from parse import parse
from geomet_data_registry.layer.base import BaseLayer
from geomet_data_registry.util import DATE_FORMAT

LOGGER = logging.getLogger(__name__)


class HrdpaLayer(BaseLayer):
    """HRDPA layer"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.layer.HrdpaLayer`
        """

        provider_def = {'name': 'hrdpa'}

        super().__init__(provider_def)

    def identify(self, filepath, url=None):
        """
        Identifies a file of the layer

        :param filepath: filepath from AMQP
        :param url: fully qualified URL of file

        :returns: `list` of file properties
        """

        super().identify(filepath, url)

        self.model = 'hrdpa'

        LOGGER.debug('Loading model information from store')
        self.file_dict = json.loads(self.store.get_key(self.model))

        filename_pattern = self.file_dict[self.model]['filename_pattern']

        tmp = parse(filename_pattern, os.path.basename(filepath))

        file_pattern_info = {
            'wx_variable': tmp.named['wx_variable'],
            'time_': tmp.named['YYYYMMDD_model_run'],
            'fh': tmp.named['forecast_hour']
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        if self.wx_variable not in self.file_dict[self.model]['variable']:
            msg = 'Variable "{}" not in ' \
                  'configuration file'.format(self.wx_variable)
            LOGGER.warning(msg)
            return False

        runs = self.file_dict[self.model]['variable'][self.wx_variable][
            'model_run']
        self.model_run_list = list(runs.keys())

        time_format = '%Y%m%d%H'
        self.date_ = datetime.strptime(file_pattern_info['time_'], time_format)

        self.model_run = '{}Z'.format(self.date_.strftime('%H'))

        forecast_hour_datetime = self.date_ + \
            timedelta(hours=int(file_pattern_info['fh']))

        member = self.file_dict[self.model]['variable'][self.wx_variable][
            'members']
        elevation = self.file_dict[self.model]['variable'][self.wx_variable][
            'elevation']
        str_fh = re.sub('[^0-9]',
                        '',
                        forecast_hour_datetime.strftime(DATE_FORMAT))
        expected_count = self.file_dict[self.model]['variable'][
            self.wx_variable]['model_run'][self.model_run]['files_expected']

        self.geomet_layers = self.file_dict[self.model]['variable'][
            self.wx_variable]['geomet_layers']
        for layer_name, layer_config in self.geomet_layers.items():
            identifier = '{}-{}'.format(layer_name, str_fh)

            forecast_hours = layer_config['forecast_hours']
            begin, end, interval = [int(re.sub(r'[^-\d]', '', value))
                                    for value in forecast_hours.split('/')]

            feature_dict = {
                'layer_name': layer_name,
                'filepath': self.filepath,
                'identifier': identifier,
                'reference_datetime': None,
                'forecast_hour_datetime': self.date_.strftime(DATE_FORMAT),
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
                'refresh_config': True,
            }
            self.items.append(feature_dict)

        return True

    def add_time_key(self):
        """
        Adds default time and time extent datetime values to store for radar
        layers. Overrides the add_time_key method of BaseLayer class due to
        radar data's lack of forecast models.
        :return: `bool` if successfully added a new radar time key
        """

        for item in self.items:

            default_time_key = '{}_default_time'.format(item['layer_name'])
            last_default_time_key = self.store.get_key(default_time_key)
            time_extent_key = '{}_time_extent'.format(item['layer_name'])

            start_time = self.date_ + timedelta(
                hours=item['forecast_hours']['begin'])
            start_time = start_time.strftime(DATE_FORMAT)
            end_time = self.date_.strftime(DATE_FORMAT)

            time_extent_value = '{}/{}/{}'.format(start_time,
                                                  end_time,
                                                  item['forecast_hours']
                                                  ['interval'])

            if last_default_time_key and datetime.strptime(
                    last_default_time_key, DATE_FORMAT) > self.date_:
                LOGGER.debug(
                    'New default time value ({}) is older than the current '
                    'default time in store: {}. '
                    'Not updating time keys.'.format(
                        end_time, last_default_time_key))
                continue

            LOGGER.debug('Adding time keys in the store')
            self.store.set_key(default_time_key, end_time)
            self.store.set_key(time_extent_key, time_extent_value)

        return True

    def __repr__(self):
        return '<HrdpaLayer> {}'.format(self.name)
