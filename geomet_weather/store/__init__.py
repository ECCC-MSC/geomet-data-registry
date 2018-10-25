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

import importlib
import logging

from geomet_weather.env import STORE_TYPE, STORE_URL
from geomet_weather.store.base import KeyValueStoreError

LOGGER = logging.getLogger(__name__)

PROVIDERS = {
    'redis': 'geomet_weather.store.redis_.RedisKeyValueStore'
}


def load_store(provider_name, provider_url):
    """
    loads key-value store by provider name

    :param provider_name: provider name
    :param provider_url: provider url

    :returns: geomet_weather.store.KeyValueStore object
    """

    LOGGER.debug('Providers: {}'.format(PROVIDERS))

    if provider_name is None:
        msg = 'provider name is required'
        LOGGER.error(msg)
        raise KeyValueStoreError(msg)

    if '.' not in provider_name and provider_name not in PROVIDERS.keys():
        msg = 'Key-value store provider {} not found'.format(provider_name)
        LOGGER.error(msg)
        raise KeyValueStoreError(msg)

    if '.' in provider_name:  # dotted path
        packagename, classname = provider_name.rsplit('.', 1)
    else:  # core provider
        packagename, classname = PROVIDERS[provider_name].rsplit('.', 1)

    LOGGER.debug('package name: {}'.format(packagename))
    LOGGER.debug('class name: {}'.format(classname))

    module = importlib.import_module(packagename)
    class_ = getattr(module, classname)
    provider = class_(provider_name, provider_url)
    return provider
