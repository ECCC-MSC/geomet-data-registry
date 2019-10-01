###############################################################################
#
# Copyright (C) 2019 Tom Kralidis
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

from geomet_data_registry.layer.base import BaseLayer, LayerError

LOGGER = logging.getLogger(__name__)


class ModelGemGlobalLayer(BaseLayer):
    """GDPS layer"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.layer.model_gem_global.ModelGemGlobalLayer`  # noqa
        """

        provider_def = {'name': 'model_gem_global'}

        BaseLayer.__init__(self, provider_def)

    def identify(self, filepath):
        """
        Identifies a file of the layer

        :param filepath: filepath from AMQP

        :returns: `list` of file properties
        """

        self.filepath = filepath
        self.file_creation_datetime = datetime.fromtimestamp(
                os.path.getmtime(filepath))
        self.model = 'model_gem_global'

        LOGGER.debug('Loading model information from store')
        file_dict = json.loads(self.store.get_key(self.model))

        filename_pattern = file_dict[self.model]['file_path_pattern']

        tmp = parse(filename_pattern, os.path.basename(filepath))

        file_pattern_info = {
            'wx_variable': tmp.named['wx_variable'],
            'time_': tmp.named['YYYYMMDD_model_run'],
            'fh': tmp.named['forecast_hour']
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        if self.wx_variable not in file_dict[self.model]['variable']:
            msg = 'Variable "{}" not in ' \
                  'configuration file'.format(self.wx_variable)
            LOGGER.exception(msg)
            raise LayerError(msg)

        runs = file_dict[self.model]['variable'][self.wx_variable]['model_run']
        self.model_run_list = list(runs.keys())

        time_format = '%Y%m%d%H'
        date_ = datetime.strptime(file_pattern_info['time_'], time_format)

        reference_datetime = date_
        self.model_run = '{}Z'.format(date_.strftime('%H'))

        forecast_hour_datetime = date_ + \
            timedelta(hours=int(file_pattern_info['fh']))

        member = file_dict[self.model]['variable'][self.wx_variable]['members']  # noqa
        elevation = file_dict[self.model]['variable'][self.wx_variable]['elevation']  # noqa
        str_mr = re.sub('[^0-9]',
                        '',
                        reference_datetime.strftime('%Y-%m-%dT%H:%M:%SZ'))
        str_fh = re.sub('[^0-9]',
                        '',
                        forecast_hour_datetime.strftime('%Y-%m-%dT%H:%M:%SZ'))
        expected_count = file_dict[self.model]['variable'][self.wx_variable]['model_run'][self.model_run]['files_expected'] # noqa

        for key, values in file_dict[self.model]['variable'][self.wx_variable]['geomet_layers'].items(): # noqa
            layer_name = key
            identifier = '{}-{}-{}'.format(layer_name, str_mr, str_fh)

            begin, end, interval = file_dict[self.model]['variable'][self.wx_variable]['geomet_layers'][key]['forecast_hours'].split('/') # noqa
            interval = re.sub('[^0-9]', '', interval)

            fh = file_pattern_info['fh']
            if int(fh) in range(int(begin), int(end), int(interval)):
                feature_dict = {
                    'layer_name': layer_name,
                    'filepath': filepath,
                    'identifier': identifier,
                    'reference_datetime': reference_datetime,
                    'forecast_hour_datetime': forecast_hour_datetime,
                    'member': member,
                    'model': self.model,
                    'elevation': elevation,
                    'expected_count': expected_count
                }

                self.items.append(feature_dict)

        return True

    def __repr__(self):
        return '<ModelGemGlobalLayer> {}'.format(self.name)
