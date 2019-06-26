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

from datetime import datetime, timedelta
import json
import logging
import parse
import re
import redis

from geomet_weather.layer.base import BaseLayer

LOGGER = logging.getLogger(__name__)


class ModelGemGlobalLayer(object):
    """generic layer ABC"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_weather.layer.base.BaseLayer`
        """

        self.elevation = None
        self.id_ = None
        self.iso_formatted_mr = None
        self.iso_formatted_fh = None
        self.layer_name = None
        self.member = None
        self.model = None
        self.wx_variable = None

        provider_def = {'name': 'model_gem_global'}

        BaseLayer.__init__(self, provider_def)

    def identify(self, filepath):
        """
        Identifies a file of the layer

        :param filepath: fielpath from AMQP

        :returns: `list` of file properties
        """

        self.model = 'model_gem_global'

        def parse_filename_wx_variable(filename_pattern):
            result = None
            while True:
                n = (yield result)
                tmp = parse.parse(filename_pattern, n)
                result = {'wx_variable': tmp.named['wx_variable'],
                          'time_': tmp.named['YYYYMMDD_self.model_run'],
                          'fh': tmp.named['forecast_hour']}

        LOGGER.debug('Loading model information from store')
        file_dict = json.loads(self.store.get(self.model))

        filename_pattern = file_dict[self.model]['file_path_pattern']
        p = parse_filename_wx_variable(filename_pattern)
        next(p)

        LOGGER.debug('Parsing filename from file path pattern')
        file_pattern_info = p.send(filepath)

        LOGGER.debug('Defining the different file properties')
        self.wx_variable = file_pattern_info['wx_variable']

        time_format = '%Y%m%d%H'
        date = datetime.strptime(file_pattern_info['time_'], time_format)

        self.iso_formatted_mr = str(date.strftime('%Y-%m-%dT%H:%M:%SZ'))

        fh = date + timedelta(hours=int(file_pattern_info['fh']))
        self.iso_formatted_fh = str(fh.strftime('%Y-%m-%dT%H:%M:%SZ'))

        self.layer_name = file_dict[self.model]['variable'][self.wx_variable]['geomet_layer']
        self.member = file_dict[self.model]['variable'][self.wx_variable]['member']
        self.elevation = file_dict[self.model]['variable'][self.wx_variable]['elevation']
        self.id_ = self.layer_name + re.sub('[^0-9]', '', self.iso_formatted_mr) + re.sub('[^0-9]', '', self.iso_formatted_fh)

        return True

    def __repr__(self):
        return '<BaseLayer> {}'.format(self.name)


class LayerError(Exception):
    """setup error"""
    pass
