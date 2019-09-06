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

import codecs
import json
import logging

import click
from yaml import load, Loader

from geomet_data_registry.env import STORE_TYPE, STORE_URL
from geomet_data_registry.plugin import load_plugin
from geomet_data_registry.store.base import StoreError

LOGGER = logging.getLogger(__name__)


@click.group()
def store():
    """Manage the geomet-data-registry store"""
    pass


@click.command()
@click.pass_context
@click.option('--group', '-g', help='group')
def setup(ctx, group=None):
    """create store"""

    provider_def = {
        'type': STORE_TYPE,
        'url': STORE_URL,
        'group': group
    }

    st = load_plugin('store', provider_def)

    try:
        click.echo('Creating store {}'.format(st.url))
        st.setup()
    except StoreError as err:
        raise click.ClickException(err)
    click.echo('Done')


@click.command()
@click.pass_context
@click.option('--group', '-g', help='group')
def teardown(ctx, group=None):
    """delete store"""

    provider_def = {
        'type': STORE_TYPE,
        'url': STORE_URL,
        'group': group
    }

    st = load_plugin('store', provider_def)

    try:
        click.echo('Deleting store {}'.format(st.url))
        st.teardown()
    except StoreError as err:
        raise click.ClickException(err)
    click.echo('Done')


@click.command('set')
@click.pass_context
@click.option('--key', '-k', help='key name for store')
@click.option('--config', '-c', 'config',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to config yaml file')
def set_key(ctx, key, config):
    """populate store"""

    provider_def = {
        'type': STORE_TYPE,
        'url': STORE_URL
    }

    st = load_plugin('store', provider_def)

    try:
        click.echo('populating store {}'.format(st.url))
        with codecs.open(config) as ff:
            yml_dict = load(ff, Loader=Loader)
            string_ = json.dumps(yml_dict)
            st.set_key(key, string_)
    except StoreError as err:
        raise click.ClickException(err)
    click.echo('Done')


store.add_command(setup)
store.add_command(teardown)
store.add_command(set_key)
