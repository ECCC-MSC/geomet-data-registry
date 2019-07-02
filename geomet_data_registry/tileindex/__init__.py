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

from geomet_data_registry.env import (
    TILEINDEX_TYPE, TILEINDEX_BASEURL, TILEINDEX_NAME)
from geomet_data_registry.plugin import load_plugin
from geomet_data_registry.tileindex.base import TileIndexError

LOGGER = logging.getLogger(__name__)


@click.group()
def tileindex():
    """Manage the geomet-data-registry tileindex"""
    pass


@click.command()
@click.pass_context
@click.option('--group', '-g', help='group')
def setup(ctx, group=None):
    """create tileindex"""

    provider_def = {
        'type': TILEINDEX_TYPE,
        'url': TILEINDEX_BASEURL,
        'name': TILEINDEX_NAME,
        'group': group
    }

    ti = load_plugin('tileindex', provider_def)

    try:
        click.echo('Creating tileindex {}'.format(ti.fullpath))
        ti.setup()
    except TileIndexError as err:
        raise click.ClickException(err)
    click.echo('Done')


@click.command()
@click.pass_context
@click.option('--group', '-g', help='group')
def teardown(ctx, group=None):
    """delete tileindex"""

    provider_def = {
        'type': TILEINDEX_TYPE,
        'url': TILEINDEX_BASEURL,
        'name': TILEINDEX_NAME,
        'group': group
    }

    ti = load_plugin('tileindex', provider_def)

    try:
        click.echo('Deleting tileindex {}'.format(ti.fullpath))
        ti.teardown()
    except TileIndexError as err:
        raise click.ClickException(err)
    click.echo('Done')


tileindex.add_command(setup)
tileindex.add_command(teardown)
