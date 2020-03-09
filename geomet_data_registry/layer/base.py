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
import logging
import os

from geomet_data_registry.env import STORE_PROVIDER_DEF, TILEINDEX_PROVIDER_DEF
from geomet_data_registry.plugin import load_plugin
from geomet_data_registry.util import (get_today_and_now, VRTDataset,
                                       DATE_FORMAT)

LOGGER = logging.getLogger(__name__)


class BaseLayer:
    """generic layer ABC"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.layer.base.BaseLayer`
        """

        # list of dictionaries
        self.items = []
        self.model_run_list = []

        self.file_creation_datetime = None
        self.receive_datetime = get_today_and_now()
        self.identify_datetime = None
        self.register_datetime = None
        self.filepath = None
        self.dimensions = None
        self.model = None
        self.model_run = None
        self.geomet_layers = None
        self.wx_variable = None
        self.date_ = None
        self.file_dict = None
        self.new_key_store = False

        self.name = provider_def['name']
        self.store = load_plugin('store', STORE_PROVIDER_DEF)
        self.tileindex = load_plugin('tileindex', TILEINDEX_PROVIDER_DEF)

    def identify(self, filepath):
        """
        Identifies a file of the layer

        :param filepath: filepath on disk

        :returns: `bool` of file properties
        """

        self.filepath = filepath
        self.file_creation_datetime = datetime.fromtimestamp(
            os.path.getmtime(filepath)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def register(self):
        """
        Registers a file into the system
        :returns: `bool` of status result
        """
        items = [item for item in self.items if item['register_status']]
        if len(items) > 1:
            item_bulk = []
            for item in items:
                item_bulk.append(self.layer2dict(item))
            LOGGER.debug('Adding to tileindex (bulk)')
            r = self.tileindex.bulk_add(item_bulk)
            status = r[items[0]['identifier']]
            item_dict = item_bulk[0]
            self.update_count(items[0], status, item_dict)
        elif len(items) == 1:
            item = items[0]
            LOGGER.debug('Adding item {}'.format(item['identifier']))
            item_dict = self.layer2dict(item)
            LOGGER.debug('Adding to tileindex')
            r = self.tileindex.add(item_dict['properties']['identifier'],
                                   item_dict)
            self.update_count(items[0], r, item_dict)
        else:
            LOGGER.error('Empty item list for {}'.format(self.filepath))
            return False

        return True

    def layer2dict(self, item):
        """
        Uses one model item to create a dictionary

        :param item: dictionary of layer property from the items list

        :returns: dictionary of file properties
        """

        feature_dict = {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [[-180, -90], [-180, 90], [180, 90],
                     [180, -90], [-180, -90]]
                ]
            },
            'properties': {
                 'identifier': item['identifier'],
                 'layer': item['layer_name'],
                 'filepath': item['filepath'],
                 'elevation': item['elevation'],
                 'member': item['member'],
                 'model': item['model'],
                 'weather_variable': self.wx_variable,
                 'forecast_hour_datetime': item['forecast_hour_datetime'],
                 'reference_datetime': item['reference_datetime'],
                 'file_creation_datetime': self.file_creation_datetime,
                 'receive_datetime': self.receive_datetime,
                 'identify_datetime': self.identify_datetime,
                 'register_datetime': self.register_datetime
            }
        }

        # overwrite feature_dict property if found in item dictionary
        # useful for UU layers for example when weather variable contains
        # multiple variables
        for key in item:
            if key in feature_dict['properties']:
                feature_dict['properties'][key] = item[key]

        return feature_dict

    def update_count(self, item, r, item_dict):
        """
        update count in store for expected files/layers

        :param item: dictionary of layer property from the items list
        :param r: (int) http status code
        :param item_dict: dictionary of layers formatted for the tileindex
        """

        if item['expected_count'] is not None and r == 201:
            layer_count_key = '{}_{}_{}_count'.format(
                self.model, self.wx_variable, self.model_run)
            current_layer_file_count = self.store.get_key(layer_count_key)

            LOGGER.debug('Adding to store')
            if current_layer_file_count is not None:
                LOGGER.debug('Incrementing count')
                new_layer_file_count = int(current_layer_file_count) + 1
                self.store.set_key(layer_count_key,
                                   new_layer_file_count)
            else:
                LOGGER.debug('Initializing count')
                new_layer_file_count = 1
                self.store.set_key(layer_count_key, 1)

            LOGGER.debug('Look if we have a complete model run')
            if int(new_layer_file_count) >= item['expected_count']:
                for mr in self.model_run_list:
                    layer_count_key_reset = '{}_{}_{}_count'.format(
                        self.model, self.wx_variable, mr)
                    self.store.set_key(layer_count_key_reset, 0)
                    self.new_key_store = True
            elif int(new_layer_file_count) == 1:
                for mr in self.model_run_list:
                    layer_count_key_reset = '{}_{}_{}_count'.format(
                        self.model, self.wx_variable, mr)
                    mr_nm = self.store.get_key(layer_count_key_reset)
                    if layer_count_key_reset != layer_count_key and \
                       mr_nm not in ['0', None]:
                        LOGGER.error('Incomplete model run: {} '
                                     '--> {} / {} files '
                                     '({})'.format(mr,
                                                   mr_nm,
                                                   item['expected_count'],
                                                   item['layer_name']))
                        self.store.set_key(layer_count_key_reset, 0)
        elif r == 201:
            self.new_key_store = True

    def check_layer_dependencies(self, layers_list, str_mr, str_fh):
        """
        Checks if all layer dependencies are available in the tileindex
        for a given model run and forecast hour.
        :param layers_list: `list` of layer dependencies
        :param str_mr: `str` of model run
        :param str_fh: `str` of forecast hour
        :returns: `list` of GeoJSON objects for all retrieved dependencies if
                   all dependencies are found otherwise returns an empty list
        """
        dependencies = [self.tileindex.get('{}-{}-{}'.format(
            layer, str_mr, str_fh)) for layer in layers_list]

        if None in dependencies:
            return []

        return dependencies

    def configure_layer_with_dependencies(self,
                                          dependencies,
                                          image_dimension,
                                          bands_order):
        """
        Create VRT and joined weather_variable string for layers
        that consist of multiple weather variables.
        :param dependencies: `list` of GeoJSON objects from tileindex
        :param image_dimension: `dict` with x and y keys
        :param bands_order: `list` of variables order in VRT
        :returns: `tuple` of VRT and combined weather variables as string
        """
        filepaths = [self.filepath] + [dependency['properties']
                                       ['filepath'] for dependency
                                       in dependencies]
        vrt = VRTDataset(
            filepaths,
            raster_x_size=image_dimension['x'],
            raster_y_size=image_dimension['y'],
            bands_order=bands_order).build()

        weather_variables = '{},{}'.format(
            self.wx_variable, ','.join(
                [dependency['properties']['weather_variable']
                 for dependency in dependencies]))

        return vrt, weather_variables

    def check_dependencies_default_mr(self, mr_datetime, dependencies):
        """
        For each dependency, verify that a default model run is available in
        the store and the value is equal to the passed model run time.
        :param dependencies: `list` of dependencies to check
        :param mr_datetime: `datetime` to compare dependencies to
        :returns: `bool` indicating if all dependencies'
                  default model run is equal to the passed mr_datetime param
        """
        results = [datetime.strptime(default_mr, DATE_FORMAT) == mr_datetime
                   if default_mr is not None else False
                   for default_mr in [self.store.get_key
                                      ('{}_default_model_run'.format(layer))
                                      for layer in dependencies]]
        return all(results)

    @staticmethod
    def is_valid_interval(fh, begin, end, interval):
        """
        Checks if a passed forecast hour is valid given begin, end and interval
        parameters. If the forecast hour is 0 and the interval is 0, the
        forecast hour is also considered valid (since Python's range function
        does not accept 0 as an interval).
        :param fh: `int` of forecast hour
        :param begin: `int` of forecast hour begin
        :param end: `int` of forecast hour end
        :param interval: `int` of forecast hour interval
        :returns: `bool` representing if the passed forecast hour is contained
                   in the passed begin/end/interval range
        """

        return any([fh == 0 and interval == 0,
                    fh in range(begin, end + 1, interval) if interval != 0
                    else False])

    def add_time_key(self):
        """
        Adds time keys (time extent, default model run and model runs extent,
        to store for layers included in self.items (a list of GeoMet
        layers modified/updated by an incoming received weather
        variable).
        :returns: `bool` if layers had their time keys updated successfully
        """
        for item in self.items:

            time_extent_key = '{}_time_extent'.format(item['layer_name'])

            start_time = self.date_ + timedelta(
                hours=item['forecast_hours']['begin'])
            end_time = self.date_ + timedelta(
                hours=item['forecast_hours']['end'])

            start_time = start_time.strftime(DATE_FORMAT)
            end_time = end_time.strftime(DATE_FORMAT)
            time_extent_value = '{}/{}/{}'.format(start_time,
                                                  end_time,
                                                  item['forecast_hours']
                                                  ['interval'])

            default_model_key = '{}_default_model_run'.format(item['layer_name'])
            stored_default_model_run = self.store.get_key(default_model_key)

            model_run_extent_key = '{}_model_run_extent'.format(
                item['layer_name'])
            retention_hours = self.file_dict[self.model][
                'model_run_retention_hours']
            interval_hours = self.file_dict[self.model][
                'model_run_interval_hours']
            default_model_run = self.date_.strftime(DATE_FORMAT)
            run_start_time = (self.date_ - timedelta(
                hours=retention_hours)).strftime(DATE_FORMAT)
            run_interval = 'PT{}H'.format(interval_hours)
            model_run_extent_value = '{}/{}/{}'.format(
                run_start_time, default_model_run, run_interval)

            if stored_default_model_run and datetime.strptime(
                    stored_default_model_run, DATE_FORMAT) > self.date_:
                LOGGER.debug('New default model run value ({}) is older '
                             'than the current value in store: {}. '
                             'Not updating time keys.'.format(
                                default_model_run, stored_default_model_run))
                continue

            if 'dependencies' in item['layer_config']:
                if not self.check_dependencies_default_mr(
                        self.date_, item['layer_config']['dependencies']):
                    LOGGER.debug(
                        'The default model run for at least one '
                        'dependency does not match. '
                        'Not updating time keys for {}'.format(
                            item['layer_name'])
                    )
                    continue

            LOGGER.debug('Adding time keys in the store')

            self.store.set_key(time_extent_key, time_extent_value)
            self.store.set_key(default_model_key, default_model_run)
            self.store.set_key(model_run_extent_key, model_run_extent_value)

        return True

    def __repr__(self):
        return '<BaseLayer> {}'.format(self.name)


class LayerError(Exception):
    """setup error"""
    pass
