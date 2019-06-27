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
from geomet_data_registry.trigger.base import BaseTriggerHandler

LOGGER = logging.getLogger(__name__)

DATASET_HANDLERS = {
    'CMC_glb': 'ModelGemGlobal'
}


class CoreTriggerHandler(BaseTriggerHandler):
    """base trigger handler"""

    def __init__(self, filepath):
        """
        initializer

        :param filepath: path to file

        :returns: `geomet_data_registry.trigger.core.CoreTriggerHandler`
        """

        self.layer_plugin = None

        BaseTriggerHandler.__init__(self, filepath)

    def handle(self):
        """handle incoming file"""

        LOGGER.debug('Detecting filename pattern')
        for key in DATASET_HANDLERS.keys():
            if key in self.filepath:
                plugin_def = {
                    'type': DATASET_HANDLERS[key],
                }
                self.layer_plugin = load_plugin('layer', plugin_def)

        if self.layer_plugin is None:
            raise RuntimeError('oops')

        if self.layer_plugin.identify(self.filepath):
            self.layer_plugin.register()

    def __repr__(self):
        return '<CoreTriggerHandler> {}'.format(self.filepath)
