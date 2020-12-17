###############################################################################
#
# Copyright (C) 2020 Etienne Pelletier
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
from celery import Celery

from geomet_data_registry.notifier.base import BaseNotifier

LOGGER = logging.getLogger(__name__)


class CeleryTaskNotifier(BaseNotifier):
    """Celery notifier"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.notifier.celery.CeleryTaskNotifier`
        """

        super().__init__(provider_def)

        self.app = Celery('geomet-mapfile', backend=self.url, broker=self.url)

    def refresh_mapfile(self, items, task_name):
        """
        Sends a refresh_mapfile task

        :returns: `bool` of notification status
        """
        for item in items:
            published = item['layer_config'].get('published', True)
            if item['refresh_config'] and published:
                self.app.send_task(
                    'refresh_mapfile', args=[item['layer_name']]
                )
        return True

    def __repr__(self):
        return '<CeleryTaskNotifier> {}'.format(self.url)
