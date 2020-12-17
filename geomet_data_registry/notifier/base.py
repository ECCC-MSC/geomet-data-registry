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

LOGGER = logging.getLogger(__name__)


class BaseNotifier:
    """generic notifier ABC"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition dict

        :returns: `geomet_data_registry.notifier.base.BaseNotifier`
        """

        self.type = provider_def['type']
        self.url = provider_def['url']

    def __repr__(self):
        return '<BaseNotifier> {}'.format(self.type)


class NotifierError(Exception):
    """setup error"""
    pass
