###############################################################################
#
# Copyright (C) 2021 Tom Kralidis
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

import os


def set_env_vars():
    os.environ['GDR_LOGGING_LOGLEVEL'] = 'ERROR'
    os.environ['GDR_LOGGING_LOGFILE'] = 'stdout'
    os.environ['GDR_BASEDIR'] = 'TODO'
    os.environ['GDR_DATADIR'] = 'TODO'
    os.environ['GDR_TILEINDEX_TYPE'] = 'TODO'
    os.environ['GDR_TILEINDEX_BASEURL'] = 'TODO'
    os.environ['GDR_TILEINDEX_NAME'] = 'TODO'
    os.environ['GDR_STORE_TYPE'] = 'TODO'
    os.environ['GDR_STORE_URL'] = 'TODO'
    os.environ['GDR_METPX_DISCARD'] = 'TODO'
    os.environ['GDR_METPX_EVENT_FILE_PY'] = 'TODO'
    os.environ['GDR_METPX_EVENT_MESSAGE_PY'] = 'TODO'
    os.environ['GDR_NOTIFICATIONS'] = 'TODO'
    os.environ['GDR_NOTIFICATIONS_TYPE'] = 'TODO'
    os.environ['GDR_NOTIFICATIONS_URL'] = 'TODO'
