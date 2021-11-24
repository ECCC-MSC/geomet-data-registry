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

from datetime import datetime, date, time, timezone, timedelta
import json
import logging
import re
from textwrap import dedent

from parse import with_pattern
from dateutil.relativedelta import relativedelta

LOGGER = logging.getLogger(__name__)

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class VRTDataset:
    """
    Object used to create VRTs. The object can be passed a list of ordered
    variable names to sort the provided file paths on and create a VRT with the
    bands in the specified list order (ex. UU layers where the U data needs
    to be the first band and the V data the second band).
    """

    def __init__(self, filepaths, raster_x_size=None, raster_y_size=None,
                 bands_order=None):
        self.vrt_dataset = [
            '<VRTDataset rasterXSize="{}" rasterYSize="{}" bands="{}">'.format(
                raster_x_size, raster_y_size, len(filepaths)),
            '</VRTDataset>'
        ]
        self.vrt_raster_band_template = '''\
        <VRTRasterBand dataType="Byte" band="{}">
            <ComplexSource>
                <SourceFilename>{}</SourceFilename>
                <SourceBand>1</SourceBand>
                <ScaleOffset>0.0</ScaleOffset>
                <ScaleRatio>1.0</ScaleRatio>
            </ComplexSource>
        </VRTRasterBand>'''
        self.filepaths = filepaths
        self.bands_order = bands_order

    def build(self):
        """
        Builds a VRT. If self.bands_order is passed during object
        instantiation,self.filepaths will be sorted according to the
        provided order and the resulting VRT will create the bands in the
        specified order.
        :returns: `str` of VRT.
        """
        if self.bands_order:
            LOGGER.debug("Sorting filepaths against provided bands order.")
            self.filepaths = sorted(self.filepaths,
                                    key=lambda fp: self.sort_band(fp))

        for index, filepath in enumerate(self.filepaths, start=1):
            self.vrt_dataset.insert(-1, self.vrt_raster_band_template.format(
                index, filepath))

        return self.collapse()

    def sort_band(self, filepath):
        """
        :param filepath: `str` representation of filepath
        :returns: `int` of new filepath position in relation to
                  self.bands_order
        """
        filepath_postion = [idx for idx, value in enumerate(self.bands_order)
                            if value in filepath]
        if len(filepath_postion) != 1:
            msg = "Band order could not be determined. Band order values do" \
                  " not match filepath or filepath matches several band " \
                  "order values."
            raise VRTDatasetError(msg)

        return filepath_postion

    def collapse(self):
        """
        Collapses VRT to a single-line string
        :return: `str` representation of VRT as single line with no whitespace
        formatting
        """
        formatted_vrt = ''
        for item in self.vrt_dataset:
            formatted_vrt += dedent(re.sub(r'>\s+<', '><', item))

        return formatted_vrt


class VRTDatasetError(Exception):
    pass


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
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')

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


def remove_prefix(text, prefix):
    """
    Utility function to remove a given prefix from a string if is present

    :param text: `str` to parse
    :param prefix: `str` to remove from text

    :returns: `str` of text without prefix, or text if no prefix found
    """
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def parse_iso8601_interval(interval):
    """
    Utility function to return a timedelta objet based on an ISO 8601
    interval (ex. PT3H or P1Y).

    :param inteval: `str` representing ISO 8601 interval

    :returns: timedelta object of ISO 8601 interval
    """
    time_, duration, unit = re.search('^P(T?)(\\d+)(.)', interval).groups()

    if time_:
        # this means the duration is a time
        if unit == 'H':
            relative_delta = timedelta(hours=int(duration))
        elif unit == 'M':
            relative_delta = timedelta(minutes=int(duration))
    else:
        # this means the duration is a date
        if unit == 'Y':
            relative_delta = relativedelta(years=int(duration))
        elif unit == 'M':
            relative_delta = relativedelta(months=int(duration))

    return relative_delta


def str2bool(value):
    """
    helper function to return Python boolean
    type (source: https://stackoverflow.com/a/715468)
    :param value: value to be evaluated
    :returns: `bool` of whether the value is boolean-ish
    """

    value2 = False

    if isinstance(value, bool):
        value2 = value
    else:
        value2 = value.lower() in ('yes', 'true', 't', '1', 'on')

    return value2


@with_pattern(r'\S+')
def parse_nonwhitespace(text):
    """
    Custom parse function to match any non-whitespace characters.
    Used to identify certain filename elements where
    parse interprets the underscore as a dividing character
    :param text: text to be parsed
    :returns: `str` of parsed text
    """
    return text
