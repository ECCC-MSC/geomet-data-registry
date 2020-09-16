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

from datetime import datetime, timedelta
import json
import logging
import os
from parse import parse
import re

from geomet_data_registry.layer.base import BaseLayer
from geomet_data_registry.util import DATE_FORMAT

LOGGER = logging.getLogger(__name__)


class Radar1kmLayer(BaseLayer):
    """radar layer"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.layer.radar_1km.Radar1kmLayer`
        """

        provider_def = {'name': 'Radar_1km'}

        super().__init__(provider_def)

    def identify(self, filepath, url=None):
        """
        Identifies a file of the layer

        :param filepath: filepath from AMQP
        :param url: fully qualified URL of file

        :returns: `list` of file properties
        """

        super().identify(filepath, url)

        self.model = 'radar'

        LOGGER.debug('Loading model information from store')
        self.file_dict = json.loads(self.store.get_key(self.model))

        filename_pattern = self.file_dict[self.model]['filename_pattern']

        tmp = parse(filename_pattern, os.path.basename(filepath))

        file_pattern_info = {
            'wx_variable': tmp.named['precipitation_type'],
            'time_': tmp.named['YYYYMMDDhhmm'],
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        if self.wx_variable not in self.file_dict[self.model]['variable']:
            msg = 'Variable "{}" not in ' 'configuration file'.format(
                self.wx_variable
            )
            LOGGER.warning(msg)
            return False

        time_format = '%Y%m%d%H%M'
        self.date_ = datetime.strptime(file_pattern_info['time_'], time_format)

        layer_config = self.file_dict[self.model]['variable'][self.wx_variable]
        layer_name = layer_config['layer_name']

        member = self.file_dict[self.model]['variable'][self.wx_variable][
            'member'
        ]
        elevation = self.file_dict[self.model]['variable'][self.wx_variable][
            'elevation'
        ]
        str_fh = re.sub('[^0-9]', '', self.date_.strftime(DATE_FORMAT))
        identifier = '{}-{}'.format(layer_name, str_fh)
        date_format = DATE_FORMAT

        feature_dict = {
            'layer_name': layer_name,
            'filepath': self.filepath,
            'identifier': identifier,
            'reference_datetime': None,
            'forecast_hour_datetime': self.date_.strftime(date_format),
            'member': member,
            'model': self.model,
            'elevation': elevation,
            'expected_count': None,
            'layer_config': layer_config,
            'register_status': True,
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

        layer_name = self.file_dict[self.model]['variable'][self.wx_variable][
            'geomet_layer'
        ]
        key_name = '{}_default_time'.format(layer_name)
        last_key = self.store.get_key(key_name)
        key_value = self.date_.strftime(DATE_FORMAT)
        extent_key = '{}_time_extent'.format(layer_name)
        start, end, interval = self.file_dict[self.model]['variable'][
            self.wx_variable
        ]['forecast_hours'].split('/')
        start_time = self.date_ + timedelta(minutes=int(start))
        start_time = start_time.strftime(DATE_FORMAT)
        extent_value = '{}/{}/{}'.format(start_time, key_value, interval)
        if last_key is None:
            LOGGER.warning('No previous time information in the store')
            self.store.set_key(key_name, key_value)
            self.store.set_key(extent_key, extent_value)
        else:
            LOGGER.debug('Adding time keys in the store')
            old_time = datetime.strptime(last_key, DATE_FORMAT)
            if old_time + timedelta(minutes=10) != self.date_:
                LOGGER.error(
                    'Missing radar between {}/{}'.format(old_time, self.date_)
                )
            self.store.set_key(key_name, key_value)
            self.store.set_key(extent_key, extent_value)

        return True

    def __repr__(self):
        return '<Radar1KM> {}'.format(self.name)
