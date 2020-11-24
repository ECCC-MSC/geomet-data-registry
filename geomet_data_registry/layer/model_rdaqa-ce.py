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

from datetime import datetime
import json
import logging
import os
from parse import parse
import re

from geomet_data_registry.layer.base import BaseLayer
from geomet_data_registry.util import DATE_FORMAT, parse_iso8601_interval

LOGGER = logging.getLogger(__name__)


class ModelRdaqaCeLayer(BaseLayer):
    """RDAQA Cumulative Effects layer"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.layer.model_rdaqa-ce.ModelRdaqaCeLayer`  # noqa
        """

        provider_def = {'name': 'model_rdaqa-ce'}

        super().__init__(provider_def)

    def identify(self, filepath, url=None):
        """
        Identifies a file of the layer

        :param filepath: filepath from AMQP
        :param url: fully qualified URL of file

        :returns: `list` of file properties
        """

        super().identify(filepath, url)

        self.model = 'model_rdaqa-ce'

        LOGGER.debug('Loading model information from store')
        self.file_dict = json.loads(self.store.get_key(self.model))

        filename_pattern = self.file_dict[self.model]['filename_pattern']

        tmp = parse(filename_pattern, os.path.basename(filepath))

        file_pattern_info = {
            'wx_variable': tmp.named['wx_variable'],
            'time_': tmp.named['YYYYMMDD_model_run'],
            'interval': tmp.named['interval'],
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']
        self.interval = file_pattern_info['interval']

        if self.wx_variable not in self.file_dict[self.model]['variable']:
            msg = 'Variable "{}" not in configuration file'.format(
                self.wx_variable
            )
            LOGGER.warning(msg)
            return False

        runs = self.file_dict[self.model]['variable'][self.wx_variable][
            'model_run'
        ]
        self.model_run_list = list(runs.keys())

        time_format = '%Y%m%dT%HZ'
        self.date_ = datetime.strptime(file_pattern_info['time_'], time_format)

        member = self.file_dict[self.model]['variable'][self.wx_variable][
            'members'
        ]
        elevation = self.file_dict[self.model]['variable'][self.wx_variable][
            'elevation'
        ]
        str_fh = re.sub('[^0-9]', '', self.date_.strftime(DATE_FORMAT))

        self.geomet_layers = self.file_dict[self.model]['variable'][
            self.wx_variable
        ]['geomet_layers']
        for layer_name, layer_config in self.geomet_layers.items():
            identifier = '{}-{}'.format(layer_name, str_fh)

            feature_dict = {
                'layer_name': layer_name,
                'filepath': self.filepath,
                'identifier': identifier,
                'reference_datetime': None,
                'forecast_hour_datetime': self.date_.strftime(DATE_FORMAT),
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
        RAQDPS-FW.CE data's lack of forecast models.
        :return: `bool` if successfully added a new radar time key
        """

        for item in self.items:
            new_date_str = self.date_.strftime(DATE_FORMAT)

            default_time_key_name = '{}_default_time'.format(
                item['layer_name']
            )
            default_extent_key_name = '{}_time_extent'.format(
                item['layer_name']
            )

            last_default_time_key = self.store.get_key(default_time_key_name)
            last_default_extent_key = self.store.get_key(
                default_extent_key_name
            )

            if last_default_time_key is None:
                LOGGER.warning('No previous time information in the store')
                self.store.set_key(default_time_key_name, new_date_str)
                self.store.set_key(
                    default_extent_key_name,
                    '{}/{}/{}'.format(
                        new_date_str, new_date_str, self.interval
                    ),
                )
            else:
                LOGGER.debug('Adding time keys in the store')
                previous_default_time = datetime.strptime(
                    last_default_time_key, DATE_FORMAT
                )
                previous_interval_begin, previous_interval_end = [
                    datetime.strptime(elem, DATE_FORMAT)
                    for elem in last_default_extent_key.split('/')[:2]
                ]

                if (
                    previous_default_time
                    + parse_iso8601_interval(self.interval)
                    != self.date_
                ):
                    LOGGER.warning(
                        'Missing RAQDPS-FW Cumulative Effects data'
                        ' between {}/{}'.format(
                            previous_default_time, self.date_
                        )
                    )

                if self.date_ < previous_interval_begin:
                    self.store.set_key(
                        default_extent_key_name,
                        '{}/{}/{}'.format(
                            new_date_str,
                            previous_interval_end.strftime(DATE_FORMAT),
                            self.interval,
                        ),
                    )

                elif self.date_ > previous_interval_end:
                    self.store.set_key(
                        default_extent_key_name,
                        '{}/{}/{}'.format(
                            previous_interval_begin.strftime(DATE_FORMAT),
                            new_date_str,
                            self.interval,
                        ),
                    )

        return True

    def __repr__(self):
        return '<ModelRdaqaCeLayer> {}'.format(self.name)
