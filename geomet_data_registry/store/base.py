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

LOGGER = logging.getLogger(__name__)


class BaseStore(object):
    """generic key-value store ABC"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.store.base.BaseStore`
        """

        self.type = provider_def['type']
        self.url = provider_def['url']

    def setup(self):
        """
        Create the store

        :returns: `bool` of process status
        """

        raise NotImplementedError()

    def teardown(self):
        """
        Delete the store

        :returns: `bool` of process status
        """

        raise NotImplementedError()

    def get_key(self, key):
        """
        Get key from store

        :param key: key to fetch

        :returns: string of key value from Redis store
        """

        raise NotImplementedError()

    def set_key(self, key, value):
        """
        Set key value from

        :param key: key to set value
        :param value: value to set

        :returns: `bool` of set success
        """

        raise NotImplementedError()

    def list_keys(self, pattern=None):
        """
        List all keys in store

        :param pattern: regular expression to filter keys on

        :returns: `list` of all store keys
        """

        raise NotImplementedError()

    def __repr__(self):
        return '<BaseStore> {}'.format(self.type)


class StoreError(Exception):
    """setup error"""
    pass
