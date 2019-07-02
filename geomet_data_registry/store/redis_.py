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

import redis

from geomet_data_registry import __version__
from geomet_data_registry.store.base import BaseStore, StoreError

LOGGER = logging.getLogger(__name__)


class RedisStore(BaseStore):
    """Redis key-value store implementation"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.store.redis_.RedisStore`
        """

        BaseStore.__init__(self, provider_def)

        try:
            self.redis = redis.Redis.from_url(self.url)
        except redis.exceptions.ConnectionError as err:
            msg = 'Cannot connect to Redis {}: {}'.format(self.url, err)
            LOGGER.exception(msg)
            raise StoreError(msg)

    def setup(self):
        """
        Create the store

        :returns: boolean of process status
        """

        return self.redis.set('geomet-data-registry-version', __version__)

    def teardown(self):
        """
        Delete the store

        :returns: boolean of process status
        """

        return self.redis.delete('geomet-data-registry-version')

    def get(self, key):
        """
        Get key from store

        :param key: key to fetch

        :returns: string of key value from Redis store
        """

        return self.redis.get(key)

    def set(self, key, value):
        """
        Set key value from

        :param key: key to set value
        :param value: value to set

        :returns: `bool` of set success
        """

        return self.redis.set(key, value)

    def __repr__(self):
        return '<BaseStore> {}'.format(self.type)
