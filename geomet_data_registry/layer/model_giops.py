###############################################################################
#
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
from parse import parse, with_pattern
import re

from geomet_data_registry.layer.base import BaseLayer
from geomet_data_registry.util import DATE_FORMAT

LOGGER = logging.getLogger(__name__)


@with_pattern(r'\S+')
def parse_fileinfo(text):
    return text


class GiopsLayer(BaseLayer):
    """GIOPS layer"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.layer.giops.GiopsLayer`
        """

        provider_def = {'name': 'giops'}
        self.model_base = 'model_giops'
        self.dimension = None  # identifies if the layer is 2D or 3D GIOPS data
        self.bands = None
        self.layer_names = []

        BaseLayer.__init__(self, provider_def)

    def identify(self, filepath):
        """
        Identifies a file of the layer

        :param filepath: filepath from AMQP

        :returns: `list` of file properties
        """

        super().identify(filepath)

        LOGGER.debug('Loading model information from store')
        self.file_dict = json.loads(self.store.get_key(self.model_base))
        filename_pattern = self.file_dict[self.model_base]['filename_pattern']

        if self.filepath.split('/')[-4] == '2d':
            self.dimension = '2D'
            self.model = 'model_giops_2D'
        elif self.filepath.split('/')[-4] == '3d':
            self.dimension = '3D'
            self.model = 'model_giops_3D'

        tmp = parse(filename_pattern, os.path.basename(filepath), dict(parse_fileinfo=parse_fileinfo))

        file_pattern_info = {
            'wx_variable': tmp.named['wx_variable'],
            'time_': tmp.named['YYYYMMDD_model_run'],
            'forecast_hour_prefix': tmp.named['forecast_hour_prefix'],
            'fh': tmp.named['forecast_hour']
        }

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        var_path = self.file_dict[self.model_base][self.dimension]['variable']
        if self.wx_variable not in var_path:
            msg = 'Variable "{}" not in ' \
                  'configuration file'.format(self.wx_variable)
            LOGGER.warning(msg)
            return False

        runs = self.file_dict[self.model_base][self.dimension]['variable'][self.wx_variable]['model_run']  # noqa
        self.model_run_list = list(runs.keys())

        weather_var = self.file_dict[self.model_base][self.dimension]['variable'][self.wx_variable]  # noqa

        time_format = '%Y%m%d%H'
        self.date_ = datetime.strptime(file_pattern_info['time_'], time_format)
        reference_datetime = self.date_
        self.model_run = '{}Z'.format(self.date_.strftime('%H'))
        forecast_hour_datetime = self.date_ + \
            timedelta(hours=int(file_pattern_info['fh']))

        if self.dimension == '3D':
            self.bands = self.file_dict[self.model_base][self.dimension]['variable'][self.wx_variable]['bands']
            for band in self.bands.keys():
                elevation = self.bands[band]['elevation']
                str_mr = re.sub('[^0-9]',
                                '',
                                reference_datetime.strftime(DATE_FORMAT))
                str_fh = re.sub('[^0-9]',
                                '',
                                forecast_hour_datetime.strftime(DATE_FORMAT))

                expected_count = self.file_dict[self.model_base][self.dimension]['variable'][self.wx_variable]['model_run'][self.model_run]['files_expected']  # noqa

                for layer in weather_var['geomet_layers'].keys():
                    member = None
                    layer_name = layer.format(self.bands[band]['product'])

                    identifier = '{}-{}-{}'.format(layer_name, str_mr, str_fh)

                    feature_dict = {
                        'layer_name': layer_name,
                        'filepath': self.filepath,
                        'identifier': identifier,
                        'reference_datetime': reference_datetime.strftime(DATE_FORMAT),  # noqa
                        'forecast_hour_datetime': forecast_hour_datetime.strftime(DATE_FORMAT),  # noqa
                        'member': member,
                        'model': self.model,
                        'elevation': elevation,
                        'expected_count': expected_count
                    }

                    self.items.append(feature_dict)
                    self.layer_names.append(layer_name)

        if self.dimension == '2D':
            elevation = weather_var['elevation']
            str_mr = re.sub('[^0-9]',
                            '',
                            reference_datetime.strftime(DATE_FORMAT))
            str_fh = re.sub('[^0-9]',
                            '',
                            forecast_hour_datetime.strftime(DATE_FORMAT))

            expected_count = self.file_dict[self.model_base][self.dimension]['variable'][self.wx_variable]['model_run'][self.model_run]['files_expected']  # noqa

            for layer in weather_var['geomet_layers'].keys():
                member = None
                identifier = '{}-{}-{}'.format(layer, str_mr, str_fh)

                feature_dict = {
                    'layer_name': layer,
                    'filepath': self.filepath,
                    'identifier': identifier,
                    'reference_datetime': reference_datetime.strftime(DATE_FORMAT),  # noqa
                    'forecast_hour_datetime': forecast_hour_datetime.strftime(DATE_FORMAT),  # noqa
                    'member': member,
                    'model': self.model,
                    'elevation': elevation,
                    'expected_count': expected_count
                }

                self.items.append(feature_dict)
                self.layer_names.append(layer)

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
        for key in self.layer_names:

            time_extent_key = '{}_time_extent'.format(key)

            wx_info = self.file_dict[self.model_base][self.dimension]['variable'][self.wx_variable]  # noqa

            for layer in wx_info['geomet_layers']:
                if key.startswith(layer.format('')):
                    start, end, interval = wx_info['geomet_layers'][layer]['forecast_hours'].split('/')  # noqa
                    start_time = self.date_ + timedelta(hours=int(start))
                    end_time = self.date_ + timedelta(hours=int(end))
                    start_time = start_time.strftime(DATE_FORMAT)
                    end_time = end_time.strftime(DATE_FORMAT)
                    time_extent_value = '{}/{}/{}'.format(start_time,
                                                          end_time,
                                                          interval)

            default_model_key = '{}_default_model_run'.format(key)
            stored_default_model_run = self.store.get_key(default_model_key)

            model_run_extent_key = '{}_model_run_extent'.format(key)
            retention_hours = self.file_dict[self.model_base]['model_run_retention_hours']  # noqa
            interval_hours = self.file_dict[self.model_base]['model_run_interval_hours']  # noqa
            default_model_run = self.date_.strftime(DATE_FORMAT)
            run_start_time = (self.date_ - timedelta(hours=retention_hours)).strftime(DATE_FORMAT)  # noqa
            run_interval = 'PT{}H'.format(interval_hours)
            model_run_extent_value = '{}/{}/{}'.format(run_start_time, default_model_run, run_interval)  # noqa

            if stored_default_model_run and datetime.strptime(stored_default_model_run, DATE_FORMAT) > self.date_:
                LOGGER.debug("New default model run value ({}) is older than the current value in store: {}. "
                             "Not updating time keys.".format(default_model_run, stored_default_model_run))
                continue

            LOGGER.debug('Adding time keys in the store - Variable: {} - Key: {} - Model run: {}'.format(key, self.wx_variable, default_model_run))

            self.store.set_key(time_extent_key, time_extent_value)
            self.store.set_key(default_model_key, default_model_run)
            self.store.set_key(model_run_extent_key, model_run_extent_value)

    def __repr__(self):
        return '<ModelGiopsLayer> {}'.format(self.name)
