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


class Event(object):
    """core event"""

    def __init__(self, parent):
        """initialize"""
        pass

    def dispatch(self, parent):
        """
        sarracenia dispatcher

        :param parent: `sarra.sr_subscribe.sr_subscribe`

        :returns: `bool` of dispatch result
        """
        try:
            from geomet_data_registry.trigger.core import CoreTriggerHandler

            filepath = parent.msg.local_file
            parent.logger.debug('Filepath: {}'.format(filepath))
            handler = CoreTriggerHandler(filepath)
            result = handler.handle()
            parent.logger.debug('Result: {}'.format(result))
            return True
        except Exception as err:
            parent.logger.warning(err)
            return False

    def __repr__(self):
        return '<Event>'


event = Event(self)
self.on_message = event.dispatch
