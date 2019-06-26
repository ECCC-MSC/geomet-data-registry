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
from geomet_weather.plugin import load_plugin
from geomet_weather.env import STORE_PROVIDER_DEF, TILEINDEX_PROVIDER_DEF

LOGGER = logging.getLogger(__name__)


class BaseLayer(object):
    """generic layer ABC"""

    def __init__(self, provider_def, filepath):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_weather.layer.base.BaseLayer`
        """

        self.name = provider_def['name']
        self.filepath = filepath
        self.store = load_plugin('store', STORE_PROVIDER_DEF)
        self.tileindex = load_plugin('tileindex', TILEINDEX_PROVIDER_DEF)

    def identify(self):
        """
        Identifies a file of the layer

        :returns: `list` of file properties
        """

        raise NotImplementedError()

    def layer2dict(self):
        return {
            'type': 'Feature',
            'ID': self.identifier,
            'geometry': {
                'type': 'Polygon',
                'coordinates': []
            },
            'properties': {
                'identifier': self.identifier,
            }
        }

    def __repr__(self):
        return '<BaseLayer> {}'.format(self.name)


class LayerError(Exception):
    """setup error"""
    pass
