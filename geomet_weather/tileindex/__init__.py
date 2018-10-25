###############################################################################
#
# Copyright (C) 2018 Tom Kralidis
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

import importlib
import logging

import click

from geomet_weather.env import TILEINDEX_TYPE, TILEINDEX_BASEURL
from geomet_weather.tileindex.base import TileIndexError

LOGGER = logging.getLogger(__name__)

PROVIDERS = {
    'Elasticsearch': 'geomet_weather.tileindex.elasticsearch_.ElasticsearchTileIndex'  # noqa
}


def load_tileindex(provider_name, provider_url, provider_group):
    """
    loads tileindex by provider name

    :param provider_name: provider name
    :param provider_url: provider url
    :param provider_group: provider group

    :returns: geomet_weather.tileindex.base.BaseTileIndex object
    """

    LOGGER.debug('Providers: {}'.format(PROVIDERS))

    if provider_name is None:
        msg = 'provider name is required'
        LOGGER.error(msg)
        raise TileIndexError(msg)

    if '.' not in provider_name and provider_name not in PROVIDERS.keys():
        msg = 'Tile index provider {} not found'.format(provider_name)
        LOGGER.error(msg)
        raise TileIndexError(msg)

    if '.' in provider_name:  # dotted path
        packagename, classname = provider_name.rsplit('.', 1)
    else:  # core provider
        packagename, classname = PROVIDERS[provider_name].rsplit('.', 1)

    LOGGER.debug('package name: {}'.format(packagename))
    LOGGER.debug('class name: {}'.format(classname))

    module = importlib.import_module(packagename)
    class_ = getattr(module, classname)
    provider = class_(provider_name, provider_url, provider_group)
    return provider


@click.group()
def tileindex():
    pass


@click.command()
@click.pass_context
@click.option('--provider', '-p', type=click.Choice(list(PROVIDERS.keys())),
              help='group')
@click.option('--group', '-g', help='group')
def create(ctx, provider=None, group=None):
    """create tileindex"""

    ti = load_tileindex(TILEINDEX_TYPE, TILEINDEX_BASEURL, group)

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

    ti = load_tileindex(TILEINDEX_TYPE, TILEINDEX_BASEURL, group)

    try:
        click.echo('Deleting tileindex {}'.format(ti.fullpath))
        ti.delete()
    except TileIndexError as err:
        raise click.ClickException(err)
    click.echo('Done')


tileindex.add_command(create)
tileindex.add_command(delete)
