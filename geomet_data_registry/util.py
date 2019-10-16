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

from datetime import datetime, date, time, timezone
import json
import logging

LOGGER = logging.getLogger(__name__)


def json_pretty_print(data):
    """
    Pretty print a JSON serialization

    :param data: `dict` of JSON

    :returns: `str` of pretty printed JSON representation
    """

    return json.dumps(data, indent=4, default=json_serial)


def json_serial(obj):
    """
    helper function to convert to JSON non-default
    types (source: https://stackoverflow.com/a/22238613)

    :param obj: `object` to be evaluate

    :returns: JSON non-default type to `str`
    """

    if isinstance(obj, (datetime, date, time)):
        serial = obj.isoformat()
        return serial

    msg = '{} type {} not serializable'.format(obj, type(obj))
    LOGGER.error(msg)
    raise TypeError(msg)


def get_today_and_now():
    """
    helper function to return a string
    of the current UTC datetime with the Z designator
    (ex. `2019-09-30T14:49:28.213142Z`)

    :returns: Current UTC datetime as `str`
    """
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
