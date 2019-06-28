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

import click

from geomet_data_registry.trigger.core import CoreTriggerHandler
from geomet_data_registry.util import json_pretty_print

LOGGER = logging.getLogger(__name__)


@click.group()
def layer():
    """Manage geomet-data-registry layers"""
    pass


@click.command('add-file')
@click.pass_context
@click.option('--file', '-f', 'file_',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to file')
@click.option('--verify', '-v', is_flag=True, help='Verify only',
              default=False)
def add_file(ctx, file_, verify=False):
    """add file to layer"""

    if file_ is None:
        raise click.ClickException('Missing --file/-f option')

    handler = CoreTriggerHandler(file_)
    result = handler.handle()

    if result:
        click.echo('File properties: {}'.format(
            json_pretty_print(handler.layer_plugin.items)))


layer.add_command(add_file)
