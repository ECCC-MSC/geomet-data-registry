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

from datetime import datetime
import logging

from geomet_data_registry.env import STORE_PROVIDER_DEF, TILEINDEX_PROVIDER_DEF
from geomet_data_registry.plugin import load_plugin

LOGGER = logging.getLogger(__name__)


class BaseLayer(object):
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
        self.receive_datetime = datetime.now()
        self.identify_datetime = None
        self.register_datetime = None
        self.filepath = None
        self.model = None
        self.model_run = None
        self.wx_variable = None

        self.name = provider_def['name']
        self.store = load_plugin('store', STORE_PROVIDER_DEF)
        self.tileindex = load_plugin('tileindex', TILEINDEX_PROVIDER_DEF)

    def identify(self, filepath):
        """
        Identifies a file of the layer

        :param filepath: filepath on disk

        :returns: `bool` of file properties
        """

    def register(self):
        """
        Registers a file into the system

        :returns: `bool` of status result
        """

        for item in self.items:
            LOGGER.debug('Adding item {}'.format(item['identifier']))

            item_dict = self.layer2dict(item)

            LOGGER.debug('Adding to tileindex')
            r = self.tileindex.add(item['identifier'], item_dict)
            if item['expected_count'] is not None and r == 201:

                layer_count_key = '{}_{}_count'.format(
                    item_dict['properties']['layer'], self.model_run)
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
                        layer_count_key_reset = '{}_{}_count'.format(
                            item_dict['properties']['layer'], mr)
                        self.store.set_key(layer_count_key_reset, 0)
                elif int(new_layer_file_count) == 1:
                    for mr in self.model_run_list:
                        layer_count_key_reset = '{}_{}_count'.format(
                            item_dict['properties']['layer'], mr)
                        if layer_count_key_reset != layer_count_key:
                            self.store.set_key(layer_count_key_reset, 0)

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
                 'forecast_hour_datetime': item['forecast_hour_datetime'],
                 'reference_datetime': item['reference_datetime'],
                 'file_creation_datetime': self.file_creation_datetime,
                 'receive_datetime': self.receive_datetime,
                 'identify_datetime': self.identify_datetime,
                 'register_datetime': self.register_datetime
            }
        }

        return feature_dict

    def __repr__(self):
        return '<BaseLayer> {}'.format(self.name)


class LayerError(Exception):
    """setup error"""
    pass
