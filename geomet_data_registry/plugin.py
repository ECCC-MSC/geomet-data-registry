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

import importlib
import logging

LOGGER = logging.getLogger(__name__)

PLUGINS = {
    'store': {
        'Redis': 'geomet_data_registry.store.redis_.RedisStore'
    },
    'tileindex': {
        'Elasticsearch': 'geomet_data_registry.tileindex.elasticsearch_.ElasticsearchTileIndex'  # noqa
    },
    'layer': {
        'ModelGemGlobal': 'geomet_data_registry.layer.model_gem_global.ModelGemGlobalLayer',  # noqa
        'Radar1km': 'geomet_data_registry.layer.radar_1km.Radar1kmLayer'  # noqa
    }
}


def load_plugin(plugin_type, plugin_def):
    """
    loads plugin by type

    :param plugin_type: type of plugin (store, tileindex, etc.)
    :param plugin_def: plugin definition

    :returns: plugin object
    """

    type_ = plugin_def['type']

    if plugin_type not in PLUGINS.keys():
        msg = 'Plugin type {} not found'.format(plugin_type)
        LOGGER.exception(msg)
        raise InvalidPluginError(msg)

    plugin_list = PLUGINS[plugin_type]

    LOGGER.debug('Plugins: {}'.format(plugin_list))

    if '.' not in type_ and type_ not in plugin_list.keys():
        msg = 'Plugin {} not found'.format(type_)
        LOGGER.exception(msg)
        raise InvalidPluginError(msg)

    if '.' in type_:  # dotted path
        packagename, classname = type_.rsplit('.', 1)
    else:  # core formatter
        packagename, classname = plugin_list[type_].rsplit('.', 1)

    LOGGER.debug('package name: {}'.format(packagename))
    LOGGER.debug('class name: {}'.format(classname))

    module = importlib.import_module(packagename)
    class_ = getattr(module, classname)
    plugin = class_(plugin_def)
    return plugin


class InvalidPluginError(Exception):
    """Invalid plugin"""
    pass
