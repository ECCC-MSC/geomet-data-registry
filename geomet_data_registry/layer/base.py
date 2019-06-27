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

        self.filepath = filepath

    def register(self):
        """
        Registers a file into the system

        :returns: `bool` of status result
        """

        for item in self.items:
            LOGGER.debug('Adding item {}'.format(item.identifier))

            item_dict = self.layer2dict(item)
            layer_count_key = '{}_{}_count'.format(
                item_dict['properties']['layer'], self.model_run)
            current_layer_file_count = self.store.get(layer_count_key)

            LOGGER.debug('Adding to store')
            if current_layer_file_count is not None:
                LOGGER.debug('Incrementing count')
                self.store.set(layer_count_key,
                               int(current_layer_file_count) + 1)
            else:
                LOGGER.debug('Initializing count')
                self.store.set(layer_count_key, 1)

            LOGGER.debug('Adding to tileindex')
            self.tileindex.add(item.identifier, item_dict)

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
                 'forecast_hour_datetime': item['forecast_hour_datetime'],
                 'reference_datetime': item['reference_datetime'],
                 'member': item['member']
            }
        }

        return feature_dict

    def __repr__(self):
        return '<BaseLayer> {}'.format(self.name)


class LayerError(Exception):
    """setup error"""
    pass
