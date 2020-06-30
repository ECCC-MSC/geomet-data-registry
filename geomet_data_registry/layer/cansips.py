###############################################################################
#
# Copyright (C) 2020 Louis-Philippe Rousseau-Lambert
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
from dateutil.relativedelta import relativedelta
import json
import logging
import os
from parse import parse
import re

from geomet_data_registry.layer.base import BaseLayer
from geomet_data_registry.util import DATE_FORMAT

LOGGER = logging.getLogger(__name__)


class CansipsLayer(BaseLayer):
    """CanSIPS layer"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.layer.cansips.CansipsLayer`  # noqa
        """

        provider_def = {'name': 'cansips'}

        super().__init__(self, provider_def)

    def identify(self, filepath, url=None):
        """
        Identifies a file of the layer

        :param filepath: filepath from AMQP
        :param url: fully qualified URL of file

        :returns: `list` of file properties
        """

        super().identify(filepath, url)

        self.model = 'cansips'

        LOGGER.debug('Loading model information from store')
        file_dict = json.loads(self.store.get_key(self.model))

        filename_pattern = file_dict[self.model]['filename_pattern']

        tmp = parse(filename_pattern, os.path.basename(filepath))

        file_pattern_info = {
            'resolution': tmp.named['resolution'],
            'wx_variable': '{}_{}_{}'.format(tmp.named['wx_variable'],
                                             tmp.named['pressure'],
                                             tmp.named['pres_value']),
            'year_': tmp.named['YYYY'],
            'month_': tmp.named['MM']
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        if self.wx_variable not in file_dict[self.model]['variable']:
            msg = 'Variable "{}" not in ' \
                  'configuration file'.format(self.wx_variable)
            LOGGER.warning(msg)
            return False

        weather_var = file_dict[self.model]['variable'][self.wx_variable]
        self.geomet_layers = weather_var['geomet_layers']

        date_format = '%Y%m'
        self.date_ = '{}{}'.format(file_pattern_info['year_'],
                                   file_pattern_info['month_'])
        reference_datetime = datetime.strptime(self.date_, date_format)
        self.date_ = reference_datetime
        self.model_run = '{}Z'.format(reference_datetime.strftime('%H'))

        for band in file_dict[self.model]['bands']:

            dict_bands = file_dict[self.model]['bands']

            fhi = dict_bands[band]['forecast_interval']
            fhi = re.sub('[^0-9]', '', fhi)

            forecast_hour_datetime = reference_datetime + \
                relativedelta(months=int(fhi))

            elevation = weather_var['elevation']
            member = dict_bands[band]['member']

            mem_str = str(member).zfill(2)

            for layer, layer_config in self.geomet_layers.items():

                layer_name = layer.format(mem_str)
                str_mr = re.sub('[^0-9]',
                                '',
                                reference_datetime.strftime(DATE_FORMAT))
                str_fh = re.sub('[^0-9]',
                                '',
                                forecast_hour_datetime.strftime(DATE_FORMAT))
                identifier = '{}-{}-{}'.format(layer_name, str_mr, str_fh)
                vrt = 'vrt://{}?bands={}'.format(self.filepath, band)

                begin, end, interval = layer_config['forecast_hours'].split(
                    '/')
                interval = int(re.sub("[^0-9]", "", interval))

                feature_dict = {
                    'layer_name': layer_name,
                    'filepath': vrt,
                    'identifier': identifier,
                    'reference_datetime': reference_datetime.strftime(
                        DATE_FORMAT),
                    'forecast_hour_datetime': forecast_hour_datetime.strftime(DATE_FORMAT), # noqa
                    'member': member,
                    'model': self.model,
                    'elevation': elevation,
                    'expected_count': None,
                    'forecast_hours': {
                        'begin': begin,
                        'end': end,
                        'interval': layer_config['forecast_hours'].split(
                            '/')[2]
                    },
                    'static_model_run': {
                        'begin': layer_config['begin']
                    },
                    'layer_config': layer_config,
                    'register_status': True
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

        for item in self.items:

            time_extent_key = '{}_time_extent'.format(item['layer_name'])

            start_time = self.date_ + relativedelta(
                months=int(item['forecast_hours']['begin']))
            end_time = self.date_ + relativedelta(
                months=int(item['forecast_hours']['end']))
            end_time = end_time.strftime(DATE_FORMAT)
            time_extent_value = '{}/{}/{}'.format(start_time,
                                                  end_time,
                                                  item['forecast_hours']
                                                  ['interval'])

            default_model_key = '{}_default_model_run'.format(
                item['layer_name'])

            model_run_extent_key = '{}_model_run_extent'.format(
                item['layer_name'])
            default_model_run = self.date_.strftime(DATE_FORMAT)
            run_start_time = item['static_model_run']['begin']
            run_interval = item['forecast_hours']['interval']
            model_run_extent_value = '{}/{}/{}'.format(run_start_time, default_model_run, run_interval)  # noqa

            LOGGER.debug('Adding time keys in the store')

            self.store.set_key(time_extent_key, time_extent_value)
            self.store.set_key(default_model_key, default_model_run)
            self.store.set_key(model_run_extent_key, model_run_extent_value)

    def __repr__(self):
        return '<ModelCanSIPSLayer> {}'.format(self.name)
