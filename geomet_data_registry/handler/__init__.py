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
import os

import click

from geomet_data_registry.handler.core import CoreHandler
from geomet_data_registry.util import json_pretty_print

LOGGER = logging.getLogger(__name__)


@click.group()
def data():
    """Manage geomet-data-registry data"""
    pass


@click.command('add')
@click.pass_context
@click.option('--file', '-f', 'file_',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to file')
@click.option('--directory', '-d', 'directory',
              type=click.Path(exists=True, resolve_path=True,
                              dir_okay=True, file_okay=False),
              help='Path to directory')
@click.option('--verify', '-v', is_flag=True, help='Verify only',
              default=False)
def add(ctx, file_, directory, verify=False):
    """add file to layer"""

    if all([file_ is None, directory is None]):
        raise click.ClickException('Missing --file/-f or --dir/-d option')

    files_to_process = []

    if file_ is not None:
        files_to_process = [file_]
    elif directory is not None:
        for root, dirs, files in os.walk(directory):
            for f in files:
                files_to_process.append(os.path.join(root, f))

    for file_to_process in files_to_process:
        handler = CoreHandler(file_to_process)
        result = handler.handle()
        if result:
            click.echo('File properties: {}'.format(
                json_pretty_print(handler.layer_plugin.items)))


data.add_command(add)
