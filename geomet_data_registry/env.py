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
import os


LOGGER = logging.getLogger(__name__)

LOGGER.info('Fetching environment variables')

LOGGING_LOGLEVEL = os.getenv('GDR_LOGGING_LOGLEVEL', 'ERROR')
LOGGING_LOGFILE = os.getenv('GDR_LOGGING_LOGFILE', None)
BASEDIR = os.environ.get('GDR_BASEDIR', None)
DATADIR = os.environ.get('GDR_DATADIR', None)
CONFIG = os.environ.get('GDR_CONFIG', None)
URL = os.environ.get('GDR_URL', None)
TILEINDEX_TYPE = os.environ.get('GDR_TILEINDEX_TYPE', None)
TILEINDEX_BASEURL = os.environ.get('GDR_TILEINDEX_BASEURL', None)
TILEINDEX_NAME = os.environ.get('GDR_TILEINDEX_NAME', None)
STORE_TYPE = os.environ.get('GDR_STORE_TYPE', None)
STORE_URL = os.environ.get('GDR_STORE_URL', None)
METPX_DISCARD = os.environ.get('GDR_METPX_DISCARD', 'on')
METPX_EVENT_PY = os.environ.get('GDR_METPX_EVENT_PY', None)

LOGGER.debug(BASEDIR)
LOGGER.debug(DATADIR)
LOGGER.debug(CONFIG)
LOGGER.debug(URL)
LOGGER.debug(TILEINDEX_TYPE)
LOGGER.debug(TILEINDEX_BASEURL)
LOGGER.debug(TILEINDEX_NAME)
LOGGER.debug(STORE_TYPE)
LOGGER.debug(STORE_URL)
LOGGER.debug(METPX_DISCARD)

if None in [BASEDIR, DATADIR, CONFIG, URL, TILEINDEX_TYPE, TILEINDEX_BASEURL,
            TILEINDEX_NAME, STORE_TYPE, STORE_URL, METPX_EVENT_PY]:
    msg = 'Environment variables not set!'
    LOGGER.error(msg)
    raise EnvironmentError(msg)

STORE_PROVIDER_DEF = {
    'type': STORE_TYPE,
    'url': STORE_URL
}

TILEINDEX_PROVIDER_DEF = {
    'type': TILEINDEX_TYPE,
    'url': TILEINDEX_BASEURL,
    'name': TILEINDEX_NAME,
    'group': None
}
