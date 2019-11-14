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

        :returns: `geomet_data_registry.layer.radar_1km.Radar1kmLayer`  # noqa
        """

        provider_def = {'name': 'Radar_1km'}

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
        self.model = 'radar'

        LOGGER.debug('Loading model information from store')
        self.file_dict = json.loads(self.store.get_key(self.model))

        filename_pattern = self.file_dict[self.model]['file_path_pattern']

        tmp = parse(filename_pattern, os.path.basename(filepath))

        file_pattern_info = {
            'wx_variable': tmp.named['precipitation_type'],
            'time_': tmp.named['YYYYMMDDhhmm']
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        if self.wx_variable not in self.file_dict[self.model]['variable']:
            msg = 'Variable "{}" not in ' \
                  'configuration file'.format(self.wx_variable)
            LOGGER.warning(msg)
            return False

        time_format = '%Y%m%d%H%M'
        self.date_ = datetime.strptime(file_pattern_info['time_'], time_format)

        self.layer_name = self.file_dict[self.model]['variable'][self.wx_variable]['geomet_layer']  # noqa

        member = self.file_dict[self.model]['variable'][self.wx_variable]['member']  # noqa
        elevation = self.file_dict[self.model]['variable'][self.wx_variable]['elevation']  # noqa
        str_fh = re.sub('[^0-9]',
                        '',
                        self.date_.strftime(DATE_FORMAT))
        identifier = '{}-{}'.format(self.layer_name, str_fh)
        date_format = DATE_FORMAT

        feature_dict = {
            'layer_name': self.layer_name,
            'filepath': filepath,
            'identifier': identifier,
            'reference_datetime': None,
            'forecast_hour_datetime': self.date_.strftime(date_format),
            'member': member,
            'model': self.model,
            'elevation': elevation,
            'expected_count': None
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

        key_name = '{}_default_time'.format(self.layer_name)
        last_key = self.store.get_key(key_name)
        key_value = self.date_.strftime(DATE_FORMAT)
        extent_key = '{}_time_extent'.format(self.layer_name)
        start, end, interval = self.file_dict[self.model]['variable'][self.wx_variable]['forecast_hours'].split('/') # noqa
        start_time = self.date_ + timedelta(minutes=int(start))
        start_time = start_time.strftime(DATE_FORMAT)
        extent_value = '{}/{}/{}'.format(start_time, key_value, interval)
        if last_key is None:
            LOGGER.warning('No previous time information in the store')
            self.store.set_key(key_name, key_value)
            self.store.set_key(extent_key, extent_value)
        else:
            LOGGER.debug('Adding time keys in the store')
            last_key = last_key.decode('utf-8')
            old_time = datetime.strptime(last_key, DATE_FORMAT)
            if old_time + timedelta(minutes=10) != self.date_:
                LOGGER.error('Missing radar between {}/{}'.format(old_time,
                                                                  self.date_))
            self.store.set_key(key_name, key_value)
            self.store.set_key(extent_key, extent_value)

    def __repr__(self):
        return '<ModelGemGlobalLayer> {}'.format(self.name)
