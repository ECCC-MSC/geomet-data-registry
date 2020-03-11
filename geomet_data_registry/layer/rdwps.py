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


class RdwpsLayer(BaseLayer):
    """RDWPS layer"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.layer.rdwps.RdwpsLayer`
        """

        provider_def = {'name': 'rdwps'}
        # self.category identifies if the RDWPS layer is a lake or gulf layer
        self.category = None

        BaseLayer.__init__(self, provider_def)

    def identify(self, filepath):
        """
        Identifies a file of the layer

        :param filepath: filepath from AMQP

        :returns: `list` of file properties
        """

        super().identify(filepath)

        self.model = 'rdwps'

        LOGGER.debug('Loading model information from store')
        self.file_dict = json.loads(self.store.get_key(self.model))

        self.category = 'lake' if 'lake' in self.filepath else 'gulf'

        filename_pattern = self.file_dict[self.model][self.category]['filename_pattern']
        tmp = parse(filename_pattern, os.path.basename(filepath))

        if self.category == 'lake':
            file_pattern_info = {
                'lake': tmp.named['lake'],
                'wx_variable': tmp.named['wx_variable'],
                'time_': tmp.named['YYYYMMDD_model_run'],
                'fh': tmp.named['forecast_hour']
            }
        elif self.category == 'gulf':
            file_pattern_info = {
                'wx_variable': tmp.named['wx_variable'],
                'time_': tmp.named['YYYYMMDD_model_run'],
                'fh': tmp.named['forecast_hour']
            }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        var_path = self.file_dict[self.model][self.category]['variable']
        if self.wx_variable not in var_path:
            msg = 'Variable "{}" not in ' \
                  'configuration file'.format(self.wx_variable)
            LOGGER.warning(msg)
            return False

        if self.category == 'lake':
            self.dimensions = self.file_dict[self.model]['dimensions'][
                file_pattern_info['lake']]
        elif self.category == 'gulf':
            self.dimensions = self.file_dict[self.model]['dimensions']['gulf']

        runs = self.file_dict[self.model][self.category]['variable'][
            self.wx_variable]['model_run']
        self.model_run_list = list(runs.keys())

        weather_var = self.file_dict[self.model][self.category]['variable'][
            self.wx_variable]

        time_format = '%Y%m%d%H'
        self.date_ = datetime.strptime(file_pattern_info['time_'], time_format)
        reference_datetime = self.date_
        self.model_run = '{}Z'.format(self.date_.strftime('%H'))
        forecast_hour_datetime = self.date_ + \
            timedelta(hours=int(file_pattern_info['fh']))

        member = self.file_dict[self.model][self.category]['variable'][
            self.wx_variable]['members']
        elevation = self.file_dict[self.model][self.category]['variable'][
            self.wx_variable]['elevation']
        str_mr = re.sub('[^0-9]',
                        '',
                        reference_datetime.strftime(DATE_FORMAT))
        str_fh = re.sub('[^0-9]',
                        '',
                        forecast_hour_datetime.strftime(DATE_FORMAT))
        expected_count = self.file_dict[self.model][self.category][
            'variable'][self.wx_variable]['model_run'][
            self.model_run]['files_expected']

        self.geomet_layers = self.file_dict[self.model][self.category][
            'variable'][self.wx_variable]['geomet_layers']
        for layer, layer_config in self.geomet_layers.items():
            layer_name = layer \
                if self.category == 'gulf' \
                else layer.format(file_pattern_info['lake'].upper())
            identifier = '{}-{}-{}'.format(layer_name, str_mr, str_fh)

            if self.category == 'lake':
                forecast_hours = layer_config['forecast_hours']
            elif self.category == 'gulf':
                forecast_hours = layer_config['forecast_hours'][
                    self.model_run]
            begin, end, interval = [int(re.sub('[^0-9]', '', value))
                                    for value in forecast_hours.split('/')]

            fh = int(file_pattern_info['fh'])

            feature_dict = {
                'layer_name': layer_name,
                'filepath': filepath,
                'identifier': identifier,
                'reference_datetime': reference_datetime.strftime(
                    DATE_FORMAT),
                'forecast_hour_datetime': forecast_hour_datetime.strftime(
                    DATE_FORMAT),
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

            if 'dependencies' in layer_config:
                if self.category == 'lake':
                    layer_config['dependencies'] = \
                        [layer.format(file_pattern_info['lake'].upper())
                         for layer in layer_config['dependencies']]
                dependencies_found = self.check_layer_dependencies(
                    layer_config['dependencies'],
                    str_mr,
                    str_fh)
                if dependencies_found:
                    bands_order = (self.file_dict[self.model]
                                   [self.category]['variable']
                                   [self.wx_variable].get('bands_order'))
                    (feature_dict['filepath'],
                     feature_dict['weather_variable']) = (
                        self.configure_layer_with_dependencies(
                            dependencies_found,
                            self.dimensions,
                            bands_order))
                else:
                    feature_dict['register_status'] = False
                    self.items.append(feature_dict)
                    continue

            if not self.is_valid_interval(fh, begin, end, interval):
                feature_dict['register_status'] = False
                LOGGER.debug('Forecast hour {} not included in {} as '
                             'defined for layer {}. File will not be '
                             'added to registry for this layer'
                             .format(fh, forecast_hours, layer_name))

            self.items.append(feature_dict)
            
        return True

    def __repr__(self):
        return '<ModelRdwpsLayer> {}'.format(self.name)
