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

LOGGER = logging.getLogger(__name__)


class BaseHandler:
    """base handler"""

    def __init__(self, filepath):
        """
        initializer

        :param filepath: path to file
        """

        self.filepath = filepath
        LOGGER.debug('Filepath: {}'.format(self.filepath))

    def handle(self):
        """handle incoming file"""

        raise NotImplementedError()

    def __repr__(self):
        return '<BaseHandler> {}'.format(self.filepath)
