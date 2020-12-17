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

from fnmatch import fnmatch
import logging
import os

from geomet_data_registry.env import NOTIFICATIONS_PROVIDER_DEF
from geomet_data_registry.plugin import load_plugin, PLUGINS
from geomet_data_registry.handler.base import BaseHandler
from geomet_data_registry.util import get_today_and_now

LOGGER = logging.getLogger(__name__)


class CoreHandler(BaseHandler):
    """base handler"""

    def __init__(self, filepath, url=None):
        """
        initializer

        :param filepath: path to file
        :param url: fully qualified URL of file

        :returns: `geomet_data_registry.handler.core.CoreHandler`
        """

        self.layer_plugin = None
        self.notification_plugin = None

        super().__init__(filepath, url)

    def handle(self):
        """
        handle incoming file

        :returns: `bool` of status result
        """

        LOGGER.debug('Detecting filename pattern')
        for key, value in PLUGINS['layer'].items():
            if fnmatch(os.path.basename(self.filepath), value['pattern']):
                plugin_def = {
                    'type': key
                }
                LOGGER.debug('Loading plugin {}'.format(plugin_def))
                self.layer_plugin = load_plugin('layer', plugin_def)

        if self.layer_plugin is None:
            msg = 'Plugin not found'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        LOGGER.debug('Identifying file')
        identify_status = self.layer_plugin.identify(self.filepath, self.url)

        if identify_status:
            self.layer_plugin.identify_datetime = get_today_and_now()
            LOGGER.debug('Registering file')
            self.layer_plugin.register()
            if self.layer_plugin.new_key_store:
                self.layer_plugin.add_time_key()

                for notifier, params in PLUGINS['notifier'].items():
                    if all([notifier == NOTIFICATIONS_PROVIDER_DEF['type'],
                           params['active']]):
                        LOGGER.debug('Loading plugin {}'.format(
                            NOTIFICATIONS_PROVIDER_DEF))
                        self.notification_plugin = load_plugin(
                            'notifier', NOTIFICATIONS_PROVIDER_DEF
                        )

                        if self.notification_plugin is None:
                            msg = 'Plugin not found'
                            LOGGER.error(msg)
                            raise RuntimeError(msg)

                        if notifier == 'Celery':
                            LOGGER.debug(
                                'Sending mapfile refresh tasks to Celery'
                            )
                            self.notification_plugin.notify(
                                self.layer_plugin.items
                            )

        return True

    def __repr__(self):
        return '<CoreHandler> {}'.format(self.url)
