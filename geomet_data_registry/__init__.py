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

__version__ = '2.3.dev0'

import click

from geomet_data_registry.layer import layer
from geomet_data_registry.store import store
from geomet_data_registry.tileindex import tileindex
from geomet_data_registry.yml_writer import expand_yml


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


cli.add_command(expand_yml)
cli.add_command(layer)
cli.add_command(store)
cli.add_command(tileindex)
