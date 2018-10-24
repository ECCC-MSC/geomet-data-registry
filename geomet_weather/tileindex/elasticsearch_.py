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

import logging
from urllib.parse import urlparse

from elasticsearch import Elasticsearch

from geomet_weather.env import TILEINDEX
from geomet_weather.tileindex.base import BaseTileIndex, TileIndexError

LOGGER = logging.getLogger(__name__)

MAPPING = {
    'settings': {
        'number_of_shards': 1,
        'number_of_replicas': 0
    },
    'mappings': {
        'FeatureCollection': {
            '_meta': {
                'geomfields': {
                    'geometry': 'POLYGON'
                }
            },
            'properties': {
                'type': {
                    'type': 'text'
                },
                'properties': {
                    'properties': {
                        'identifier': {
                            'type': 'text',
                            'fields': {
                                'raw': {'type': 'keyword'}
                            }
                        },
                        'group': {
                            'type': 'text',
                            'fields': {
                                'raw': {'type': 'keyword'}
                            }
                        },
                        'dim_reference_time': {
                            'type': 'text',
                            'fields': {
                                'raw': {'type': 'keyword'}
                            }
                        },
                        'dim_member': {
                            'type': 'text',
                            'fields': {
                                'raw': {'type': 'keyword'}
                            }
                        },
                        'dim_pressure_leel': {
                            'type': 'text',
                            'fields': {
                                'raw': {'type': 'keyword'}
                            }
                        },
                        'dim_depath': {
                            'type': 'text',
                            'fields': {
                                'raw': {'type': 'keyword'}
                            }
                        },
                        'timestamp': {
                            'type': 'date',
                            'format': 'yyyy-MM-dd HH:mm:ss'
                        },
                        'geometry': {
                            'type': 'geo_shape'
                        }
                    }
                }
            }
        }
    }
}


class ElasticsearchTileIndex(BaseTileIndex):
    """Elasticsearch TileIndex"""

    def __init__(self, provider_name):
        """
        Initialize object

        :provider_name: provider name
        :returns: pygeoapi.providers.elasticsearch_.ElasticsearchProvider
        """

        BaseTileIndex.__init__(self, provider_name)

        u = urlparse(TILEINDEX)

        url_tokens = TILEINDEX.split('/')

        LOGGER.debug('Setting Elasticsearch properties')
        self.es_host = url_tokens[2]
        self.index_name = url_tokens[-2]
        self.type_name = url_tokens[-1]
        LOGGER.debug('host: {}'.format(self.es_host))
        LOGGER.debug('index: {}'.format(self.index_name))
        LOGGER.debug('type: {}'.format(self.type_name))

        print(self.es_host)
        LOGGER.debug('Connecting to Elasticsearch')

        if u.path is not None:
            self.es = Elasticsearch(self.es_host, url_prefix=u.path)
        else:
            self.es = Elasticsearch(self.es_host)

        if not self.es.ping():
            msg = 'Cannot connect to Elasticsearch'
            LOGGER.error(msg)
            raise TileIndexError(msg)

    def __repr__(self):
        return '<ElasticsearchTileIndex> {}'.format(TILEINDEX)
