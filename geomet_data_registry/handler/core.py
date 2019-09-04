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

from datetime import datetime
import logging

from geomet_data_registry.plugin import load_plugin
from geomet_data_registry.handler.base import BaseHandler

LOGGER = logging.getLogger(__name__)

DATASET_HANDLERS = {
    'CMC_glb': 'ModelGemGlobal',
    'RADAR_COMPOSITE_1KM': 'Radar1km',
    'cansips': 'CanSIPS'
}


class CoreHandler(BaseHandler):
    """base handler"""

    def __init__(self, filepath):
        """
        initializer

        :param filepath: path to file

        :returns: `geomet_data_registry.handler.core.CoreHandler`
        """

        self.layer_plugin = None

        BaseHandler.__init__(self, filepath)

    def handle(self):
        """
        handle incoming file

        :returns: `bool` of status result
        """

        LOGGER.debug('Detecting filename pattern')
        for key in DATASET_HANDLERS.keys():
            if key in self.filepath:
                plugin_def = {
                    'type': DATASET_HANDLERS[key],
                }
                LOGGER.debug('Loading plugin {}'.format(plugin_def))
                self.layer_plugin = load_plugin('layer', plugin_def)

        if self.layer_plugin is None:
            msg = 'Plugin not found'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        LOGGER.debug('Identifying file')
        identify_status = self.layer_plugin.identify(self.filepath)

        if identify_status:
            self.layer_plugin.identify_datetime = datetime.now().isoformat()

            LOGGER.debug('Registering file')
            register_status = self.layer_plugin.register()

            if register_status:
                register_datetime_ = datetime.now()
                self.layer_plugin.register_datetime = register_datetime_

                query_dict = {
                    'filepath': self.layer_plugin.filepath
                }
                update_dict = {
                    'register_datetime': register_datetime_
                }

                self.layer_plugin.tileindex.update_by_query(
                    query_dict, update_dict)

        return True

    def __repr__(self):
        return '<CoreHandler> {}'.format(self.filepath)
