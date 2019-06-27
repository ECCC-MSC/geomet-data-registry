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

import json
import logging

import click

from geomet_data_registry.plugin import load_plugin
from geomet_data_registry.util import json_serial

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

    lyr = load_plugin('layer', {'name': 'GDPS', 'type': 'ModelGemGlobal'})

    click.echo('Adding {}'.format(file_))
    click.echo('Identifying')
    status = lyr.identify(file_)

    if not status:
        msg = 'Could not identify file {}: {}'.format(file_)
        LOGGER.exception(msg)
        raise click.ClickException(msg)

    click.echo('File properties: {}'.format(json.dumps(lyr.items, indent=4,
                                            default=json_serial)))

    if not verify:
        click.echo('Registering')
        lyr.register()


layer.add_command(add_file)
