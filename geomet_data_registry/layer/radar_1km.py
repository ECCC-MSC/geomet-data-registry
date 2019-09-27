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
import json
import logging
import os
from parse import parse
import re

from geomet_data_registry.layer.base import BaseLayer, LayerError

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

        self.model = 'radar'
        self.filepath = filepath    
    
        LOGGER.debug('Loading model information from store')
        file_dict = json.loads(self.store.get_key(self.model))

        filename_pattern = file_dict[self.model]['file_path_pattern']

        tmp = parse(filename_pattern, os.path.basename(filepath))

        file_pattern_info = {
            'wx_variable': tmp.named['precipitation_type'],
            'time_': tmp.named['YYYYMMDDhhmm']
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        if self.wx_variable not in file_dict[self.model]['variable']:
            msg = 'Variable "{}" not in ' \
                  'configuration file'.format(self.wx_variable)
            LOGGER.warning(msg)
            return False

        time_format = '%Y%m%d%H%M'
        date_ = datetime.strptime(file_pattern_info['time_'], time_format)

        layer_name = file_dict[self.model]['variable'][self.wx_variable]['geomet_layer']  # noqa

        member = file_dict[self.model]['variable'][self.wx_variable]['member']  # noqa
        elevation = file_dict[self.model]['variable'][self.wx_variable]['elevation']  # noqa
        str_fh = re.sub('[^0-9]',
                        '',
                        date_.strftime('%Y-%m-%dT%H:%M:%SZ'))
        identifier = '{}-{}'.format(layer_name, str_fh)

        feature_dict = {
            'layer_name': layer_name,
            'filepath': filepath,
            'identifier': identifier,
            'reference_datetime': None,
            'forecast_hour_datetime': date_,
            'member': member,
            'model': self.model,
            'elevation': elevation,
            'expected_count': None
        }
        self.items.append(feature_dict)

        return True

    def __repr__(self):
        return '<ModelGemGlobalLayer> {}'.format(self.name)
