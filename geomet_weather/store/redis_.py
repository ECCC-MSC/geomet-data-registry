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

from geomet_weather import __version__
from geomet_weather.store.base import BaseStore, StoreError

LOGGER = logging.getLogger(__name__)


class RedisStore(BaseStore):
    """Redis key-value store implementation"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_weather.store.redis_.RedisStore`
        """

        BaseStore.__init__(self, provider_def)

        try:
            self.redis = redis.Redis.from_url(self.url)
        except redis.exceptions.ConnectionError as err:
            msg = 'Cannot connect to Redis {}: {}'.format(self.url, err)
            LOGGER.exception(msg)
            raise StoreError(msg)

    def create(self):
        """
        Create the store

        :returns: boolean of process status
        """

        return self.redis.set('geomet-weather-version', __version__)

    def get(self, key):
        """
        Get key from store
        
        :param key: key to fetch

        :returns: string of key value from Redis store

        """

        return self.redis.get(key)

    def delete(self):
        """
        Delete the store

        :returns: boolean of process status
        """

        return self.redis.delete('geomet-weather-version')

    def __repr__(self):
        return '<BaseStore> {}'.format(self.type)
