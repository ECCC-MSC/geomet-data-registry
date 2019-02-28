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

from geomet_weather.env import (STORE_PROVIDER_DEF, TILEINDEX_PROVIDER_DEF)
from geomet_weather.layer.base import LayerError
from geomet_weather.plugin import load_plugin

LOGGER = logging.getLogger(__name__)


@click.group()
def layer():
    """Manage geomet-weather layers"""
    pass


@click.command('add-file')
@click.pass_context
@click.option('--file', '-f', 'file_',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to file')
def add_file(ctx, file_):
    """add file to layer"""

    if file_ is None:
        raise click.ClickException('Missing --file/-f option')

    lyr = load_plugin('layer', {'name': 'GDPS', 'type': 'GDPS'})

    click.echo('Identifying {}'.format(file_))
    try:
        file_properties = lyr.identify(file_)
    except LayerError as err:
        msg = 'Could not identify file {}: {}'.format(file_, err)
        LOGGER.exception(msg)
        raise click.ClickException(msg)


layer.add_command(add_file)
