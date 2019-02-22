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

from geomet_weather.env import TILEINDEX_TYPE, TILEINDEX_BASEURL
from geomet_weather.plugin import PLUGINS, load_plugin
from geomet_weather.tileindex.base import TileIndexError

LOGGER = logging.getLogger(__name__)


@click.group()
def tileindex():
    """Manage the geomet-weather tileindex"""
    pass


@click.command()
@click.pass_context
@click.option('--provider', '-p', type=click.Choice(list(PLUGINS.keys())),
              help='group')
@click.option('--group', '-g', help='group')
def create(ctx, provider=None, group=None):
    """create tileindex"""

    provider_def = {
        'type': TILEINDEX_TYPE,
        'url': TILEINDEX_BASEURL,
        'group': group
    }

    ti = load_plugin('tileindex', provider_def)

    try:
        click.echo('Creating tileindex {}'.format(ti.fullpath))
        ti.create()
    except TileIndexError as err:
        raise click.ClickException(err)
    click.echo('Done')


@click.command()
@click.pass_context
@click.option('--group', '-g', help='group')
def delete(ctx, group=None):
    """delete tileindex"""

    provider_def = {
        'type': TILEINDEX_TYPE,
        'url': TILEINDEX_BASEURL,
        'group': group
    }

    ti = load_plugin('tileindex', provider_def)

    try:
        click.echo('Deleting tileindex {}'.format(ti.fullpath))
        ti.delete()
    except TileIndexError as err:
        raise click.ClickException(err)
    click.echo('Done')


tileindex.add_command(create)
tileindex.add_command(delete)
