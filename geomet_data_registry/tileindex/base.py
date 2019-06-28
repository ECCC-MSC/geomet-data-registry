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
import os

LOGGER = logging.getLogger(__name__)


class BaseTileIndex(object):
    """generic Tile Index ABC"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider: provider definition dict
        :param url: url/path of tile index
        :param group: provider group

        :returns: `geomet_data_registry.tileindex.base.BaseTileIndex`
        """

        self.type = provider_def['type']
        self.url = provider_def['url']
        self.name = 'geomet-data-registry-tileindex-etienne'
        self.group = None

        LOGGER.debug('Detecting group tileindex')
        if 'group' in provider_def:
            self.group = provider_def['group']

        if self.group is not None:
            self.name = '{}-{}'.format(self.name, self.group)

        self.fullpath = os.path.join(self.url, self.name)

    def create(self):
        """
        Create the tileindex

        :returns: boolean of process status
        """

        raise NotImplementedError()

    def delete(self):
        """
        Delete the tileindex

        :returns: boolean of process status
        """

        raise NotImplementedError()

    def query(self):
        """
        Query the tileindex

        :returns: dict of 0..n GeoJSON features
        """

        raise NotImplementedError()

    def get(self, identifier):
        """
        Query the tileindex by identifier

        :param identifier: tileindex item identifier

        :returns: dict of single GeoJSON feature
        """

        raise NotImplementedError()

    def add(self, identifier, data):
        """
        Add an item to the tileindex

        :param identifier: tileindex item identifier
        :param data: GeoJSON dict

        :returns: boolean of process status
        """

        raise NotImplementedError()

    def remove(self, identifier):
        """
        Remove an item from the tileindex

        :param identifier: tileindex item identifier

        :returns: boolean of process status
        """

        raise NotImplementedError()

    def __repr__(self):
        return '<BaseTileIndex> {}'.format(self.type)


class TileIndexError(Exception):
    """setup error"""
    pass
