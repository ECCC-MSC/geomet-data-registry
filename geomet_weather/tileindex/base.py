###############################################################################
#
# Copyright (C) 2018 Tom Kralidis
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

LOGGER = logging.getLogger(__name__)


class BaseTileIndex(object):
    """generic Tile Index ABC"""

    def __init__(self, provider):
        """
        Initialize object

        :param type: provider type

        :returns: geomet_weather.tileindex.base.BaseTileIndex
        """

        self.type = provider

    def create(self, group=None):
        """
        Create the tileindex

        :param group: group name

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

        :param identifier: tileindex item id
        :param data: GeoJSON dict

        :returns: boolean of process status
        """

        raise NotImplementedError()

    def remove(self, identifier):
        """
        Remove an item from the tileindex

        :param identifier: identifier

        :returns: boolean of process status
        """

        raise NotImplementedError()

    def __repr__(self):
        return '<TileIndex> {}'.format(self.type)


class TileIndexError(Exception):
    """setup error"""
    pass
