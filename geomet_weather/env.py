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

BASEDIR = os.environ.get('GEOMET_WEATHER_BASEDIR', None)
DATADIR = os.environ.get('GEOMET_WEATHER_DATADIR', None)
CONFIG = os.environ.get('GEOMET_WEATHER_CONFIG', None)
URL = os.environ.get('GEOMET_WEATHER_URL', None)
TILEINDEX = os.environ.get('GEOMET_WEATHER_TILEINDEX', None)

LOGGER.debug(BASEDIR)
LOGGER.debug(DATADIR)
LOGGER.debug(CONFIG)
LOGGER.debug(URL)
LOGGER.debug(TILEINDEX)

if None in [BASEDIR, DATADIR, CONFIG, URL, TILEINDEX]:
    msg = 'Environment variables not set!'
    LOGGER.exception(msg)
    raise EnvironmentError(msg)
