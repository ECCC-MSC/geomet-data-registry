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

from geomet_data_registry.plugin import load_plugin
from geomet_data_registry.handler.base import BaseHandler
from geomet_data_registry.util import get_today_and_now
LOGGER = logging.getLogger(__name__)

DATASET_HANDLERS = {
    'CMC_glb': 'ModelGemGlobal',
    'CMC_giops': 'GIOPS',
    'CMC_reg': 'ModelGemRegional',
    'CMC_hrdps_continental': 'ModelHrdpsContinental',
    'RADAR_COMPOSITE_1KM': 'Radar1km',
    'cansips': 'CanSIPS',
    'reps': 'REPS',
    'geps': 'GEPS',
    'CMC_coupled-rdps-stlawrence': 'CGSL'
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
            self.layer_plugin.identify_datetime = get_today_and_now()
            LOGGER.debug('Registering file')
            self.layer_plugin.register()
            if self.layer_plugin.new_key_store:
                self.layer_plugin.add_time_key()
        return True

    def __repr__(self):
        return '<CoreHandler> {}'.format(self.filepath)
