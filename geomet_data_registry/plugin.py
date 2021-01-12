###############################################################################
#
# Copyright (C) 2021 Tom Kralidis
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
        'Redis': {
            'path': 'geomet_data_registry.store.redis_.RedisStore'
        }
    },
    'tileindex': {
        'Elasticsearch': {
            'path': 'geomet_data_registry.tileindex.elasticsearch_.ElasticsearchTileIndex'  # noqa
        }
    },
    'notifier': {
        'Celery': {
            'path': 'geomet_data_registry.notifier.celery_.CeleryTaskNotifier'
        }
    },
    'layer': {
        'ModelGemGlobal': {
            'pattern': 'CMC_glb*',
            'path': 'geomet_data_registry.layer.model_gem_global.ModelGemGlobalLayer',  # noqa
        },
        'ModelGemRegional': {
            'pattern': 'CMC_reg*',
            'path': 'geomet_data_registry.layer.model_gem_regional.ModelGemRegionalLayer',  # noqa
        },
        'ModelHrdpsContinental': {
            'pattern': 'CMC_hrdps_continental*',
            'path': 'geomet_data_registry.layer.model_hrdps_continental.ModelHrdpsContinentalLayer',  # noqa
        },
        'Radar1km': {
            'pattern': '*RADAR_COMPOSITE_1KM*',
            'path': 'geomet_data_registry.layer.radar_1km.Radar1kmLayer',
        },
        'CanSIPS': {
            'pattern': 'cansips*',
            'path': 'geomet_data_registry.layer.cansips.CansipsLayer',
        },
        'REPS': {
            'pattern': 'CMC-reps*',
            'path': 'geomet_data_registry.layer.reps.RepsLayer',
        },
        'GEPS': {
            'pattern': 'CMC-geps*',
            'path': 'geomet_data_registry.layer.geps.GepsLayer',
        },
        'GIOPS': {
            'pattern': 'CMC_giops*',
            'path': 'geomet_data_registry.layer.model_giops.GiopsLayer',
        },
        'CGSL': {
            'pattern': 'CMC_coupled-rdps-stlawrence*',
            'path': 'geomet_data_registry.layer.cgsl.CgslLayer',
        },
        'RDWPS': {
            'pattern': 'CMC_rdwps*',
            'path': 'geomet_data_registry.layer.rdwps.RdwpsLayer',
        },
        'GDWPS': {
            'pattern': 'CMC_gdwps_global*',
            'path': 'geomet_data_registry.layer.gdwps.GdwpsLayer',
        },
        'WCPS': {
            'pattern': 'CMC_wcps*',
            'path': 'geomet_data_registry.layer.wcps.WcpsLayer',
        },
        'HRDPA': {
            'pattern': 'CMC_HRDPA*',
            'path': 'geomet_data_registry.layer.hrdpa.HrdpaLayer',
        },
        'RDPA': {
            'pattern': 'CMC_RDPA*',
            'path': 'geomet_data_registry.layer.rdpa.RdpaLayer',
        },
        'RAQDPS': {
            'pattern': '*MSC_RAQDPS*',
            'path': 'geomet_data_registry.layer.model_raqdps.ModelRaqdpsLayer',
        },
        'RAQDPS-FW': {
            'pattern': '*MSC_RAQDPS-FW_*.grib2',
            'path': 'geomet_data_registry.layer.model_raqdps_fw.ModelRaqdpsFwLayer',  # noqa
        },
        'RAQDPS-FW-Cumulative-Effects': {
            'pattern': '*MSC_RAQDPS-FW*.nc',
            'path': 'geomet_data_registry.layer.model_raqdps_fw_ce.ModelRaqdpsFwCeLayer',  # noqa
        },
        'RDAQA-Cumulative-Effects': {
            'pattern': '*MSC_RDAQA*.nc',
            'path': 'geomet_data_registry.layer.model_rdaqa_ce.ModelRdaqaCeLayer',  # noqa
        },
    },
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
        packagename, classname = type_['path'].rsplit('.', 1)
    else:  # core formatter
        packagename, classname = plugin_list[type_]['path'].rsplit('.', 1)

    LOGGER.debug('package name: {}'.format(packagename))
    LOGGER.debug('class name: {}'.format(classname))

    module = importlib.import_module(packagename)
    class_ = getattr(module, classname)
    plugin = class_(plugin_def)
    return plugin


class InvalidPluginError(Exception):
    """Invalid plugin"""
    pass
