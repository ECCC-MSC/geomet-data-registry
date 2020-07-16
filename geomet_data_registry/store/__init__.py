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
from geomet_data_registry.util import json_pretty_print, remove_prefix

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
        click.echo(err)
    click.echo('Done')


@click.command('set')
@click.pass_context
@click.option('--key', '-k', help='key name for store')
@click.option('--config', '-c', 'config',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to config yaml file')
@click.option('--raw', '-r', is_flag=True,
              help='set key without adding prefix')
def set_key(ctx, key, config, raw):
    """populate store"""

    if all([key is None, config is None]):
        raise click.ClickException('Missing --key/-k or --config/-c option')

    provider_def = {'type': STORE_TYPE, 'url': STORE_URL}

    st = load_plugin('store', provider_def)

    try:
        with codecs.open(config) as ff:
            yml_dict = load(ff, Loader=Loader)
            string_ = json.dumps(yml_dict)
            if raw:
                click.echo('Setting {} key in store ({}).'.format(key, st.url))
                st.set_key(key, string_, raw=True)
            else:
                click.echo(
                    'Setting geomet-data-registry_{} key in store ({}).'
                    .format(key, st.url)
                )
                st.set_key(key, string_)
    except StoreError as err:
        raise click.ClickException(err)
    click.echo('Done')


@click.command('get')
@click.pass_context
@click.option('--key', '-k', help='key name to retrieve from store')
@click.option('--raw', '-r', is_flag=True,
              help='get key without adding prefix')
def get_key(ctx, key, raw):
    """get key from store"""

    if all([key is None]):
        raise click.ClickException('Missing --key/-k')

    provider_def = {
        'type': STORE_TYPE,
        'url': STORE_URL
    }

    st = load_plugin('store', provider_def)

    try:
        if raw:
            click.echo('Getting {} key from store ({}).'.format(key, st.url))
            retrieved_key = st.get_key(key, raw=True)
        else:
            click.echo(
                'Getting geomet-data-registry_{} key from store ({}).'.format(
                    key, st.url)
            )
            retrieved_key = st.get_key(key)
        if retrieved_key:
            try:
                click.echo('{}'.format(
                    json_pretty_print(json.loads(retrieved_key))))
            except ValueError:
                click.echo(retrieved_key)

    except StoreError as err:
        raise click.ClickException(err)
    click.echo('Done')


@click.command('list')
@click.option('--pattern', '-p',
              help='regular expression to filter keys on')
@click.option('--raw', '-r', is_flag=True,
              help='list raw keys without removing prefix')
@click.pass_context
def list_keys(ctx, raw, pattern=None):
    """list all keys in store"""

    provider_def = {
        'type': STORE_TYPE,
        'url': STORE_URL
    }

    st = load_plugin('store', provider_def)

    try:
        pattern = 'geomet-data-registry*{}'.format(pattern if pattern else '')
        if raw:
            keys = st.list_keys(pattern)
        else:
            keys = [remove_prefix(key, 'geomet-data-registry_') for key
                    in st.list_keys(pattern)]
        click.echo(json_pretty_print(keys))
    except StoreError as err:
        raise click.ClickException(err)
    click.echo('Done')


store.add_command(setup)
store.add_command(teardown)
store.add_command(set_key)
store.add_command(get_key)
store.add_command(list_keys)
