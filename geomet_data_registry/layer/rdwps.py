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
from geomet_data_registry.util import DATE_FORMAT, parse_nonwhitespace

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
        # self.region identifies the RDWPS region
        # (Atlantic-North-West, Erie, Superior, etc.)
        self.region = None
        self.spatial_resolution = None

        super().__init__(provider_def)

    def identify(self, filepath, url=None):
        """
        Identifies a file of the layer

        :param filepath: filepath from AMQP
        :param url: fully qualified URL of file

        :returns: `list` of file properties
        """

        super().identify(filepath, url)

        self.model = 'rdwps'

        LOGGER.debug('Loading model information from store')
        self.file_dict = json.loads(self.store.get_key(self.model))

        filename_pattern = self.file_dict[self.model]['filename_pattern']

        tmp = parse(
            filename_pattern,
            os.path.basename(filepath),
            dict(NonWhitespaceChars=parse_nonwhitespace)
        )

        file_pattern_info = {
            'region': tmp.named['region'],
            'wx_variable': tmp.named['wx_variable'],
            'date': tmp.named['YYYYMMDD'],
            'model_run': tmp.named['model_run'],
            'fh': tmp.named['forecast_hour']
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        var_path = self.file_dict[self.model]['variable']
        if self.wx_variable not in var_path:
            msg = 'Variable "{}" not in configuration file'.format(
                self.wx_variable
            )
            LOGGER.warning(msg)
            return False

        self.region = (
            file_pattern_info['region'].replace('Lake-', '')
            if file_pattern_info['region'].startswith('Lake-')
            else file_pattern_info['region']
        )

        self.dimensions = self.file_dict[self.model]['dimensions'][self.region]

        self.spatial_resolution = (
            '5km' if self.region == 'Atlantic-North-West' else '1km'
        )

        runs = self.file_dict[self.model]['variable'][self.wx_variable]['model_run']  # noqa
        self.model_run_list = list(runs.keys())

        self.date_ = datetime.strptime(
            '{}{}'.format(
                file_pattern_info['date'], file_pattern_info['model_run'],
            ),
            '%Y%m%d%H',
        )

        reference_datetime = self.date_
        self.model_run = '{}Z'.format(file_pattern_info['model_run'])
        forecast_hour_datetime = self.date_ + timedelta(
            hours=int(file_pattern_info['fh'])
        )

        member = self.file_dict[self.model]['variable'][self.wx_variable]['members']  # noqa
        elevation = self.file_dict[self.model]['variable'][self.wx_variable]['elevation']  # noqa
        str_mr = re.sub('[^0-9]', '', reference_datetime.strftime(DATE_FORMAT))
        str_fh = re.sub(
            '[^0-9]', '', forecast_hour_datetime.strftime(DATE_FORMAT)
        )
        expected_count = self.file_dict[self.model]['variable'][self.wx_variable]['model_run'][self.model_run]['files_expected']  # noqa

        self.geomet_layers = self.file_dict[self.model]['variable'][self.wx_variable]['geomet_layers']  # noqa
        for layer, layer_config in self.geomet_layers.items():
            layer_name = layer.format(self.region, self.spatial_resolution)
            identifier = '{}-{}-{}'.format(layer_name, str_mr, str_fh)
            forecast_hours = layer_config['forecast_hours']
            begin, end, interval = [
                int(re.sub('[^0-9]', '', value))
                for value in forecast_hours.split('/')
            ]

            fh = int(file_pattern_info['fh'])

            feature_dict = {
                'layer_name': layer_name,
                'filepath': self.filepath,
                'identifier': identifier,
                'reference_datetime': reference_datetime.strftime(DATE_FORMAT),
                'forecast_hour_datetime': forecast_hour_datetime.strftime(
                    DATE_FORMAT
                ),
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
                'refresh_config': True
            }

            if 'dependencies' in layer_config:
                layer_config['dependencies'] = [
                    layer.format(self.region, self.spatial_resolution)
                    for layer in layer_config['dependencies']
                ]
                dependencies_found = self.check_layer_dependencies(
                    layer_config['dependencies'], str_mr, str_fh
                )
                if dependencies_found:
                    bands_order = self.file_dict[self.model]['variable'][self.wx_variable].get('bands_order')  # noqa
                    (
                        feature_dict['filepath'],
                        feature_dict['url'],
                        feature_dict['weather_variable'],
                    ) = self.configure_layer_with_dependencies(
                        dependencies_found, self.dimensions, bands_order
                    )
                else:
                    feature_dict['register_status'] = False
                    self.items.append(feature_dict)
                    continue

            if not self.is_valid_interval(fh, begin, end, interval):
                feature_dict['register_status'] = False
                LOGGER.debug(
                    'Forecast hour {} not included in {} as '
                    'defined for layer {}. File will not be '
                    'added to registry for this layer'.format(
                        fh, forecast_hours, layer_name
                    )
                )

            self.items.append(feature_dict)

        return True

    def __repr__(self):
        return '<ModelRdwpsLayer> {}'.format(self.name)
