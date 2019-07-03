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
from urllib.parse import urlparse

from elasticsearch import Elasticsearch, exceptions

from geomet_data_registry.tileindex.base import BaseTileIndex, TileIndexError
from geomet_data_registry.util import json_pretty_print

LOGGER = logging.getLogger(__name__)

INDEX_SETTINGS = {
    'settings': {
        'index': {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
    },
    'mappings': {
        'properties': {
            'type': {
                'type': 'text'
            },
            'properties': {
                'properties': {
                    'identifier': {
                        'type': 'text',
                        'fields': {
                            'raw': {
                                'type': 'keyword'
                            }
                        }
                    },
                    'layer': {
                        'type': 'text',
                        'fields': {
                            'raw': {
                                'type': 'keyword'
                            }
                        }
                    },
                    'filepath': {
                        'type': 'text',
                        'fields': {
                            'raw': {
                                'type': 'keyword'
                            }
                        }
                    },
                    'forecast_hour_datetime': {
                        'type': 'date',
                    },
                    'reference_datetime': {
                        'type': 'date',
                    },
                    'file_creation_datetime': {
                        'type': 'date',
                    },
                    'receive_datetime': {
                        'type': 'date',
                    },
                    'identify_datetime': {
                        'type': 'date',
                    },
                    'register_datetime': {
                        'type': 'date',
                    },
                    'expiry_datetime': {
                        'type': 'date',
                    },
                    'elevation': {
                        'type': 'text',
                        'fields': {
                             'raw': {
                                 'type': 'keyword'
                             }
                         }
                    },
                    'members': {
                        'type': 'integer'
                    }
                }
            },
            'geometry': {
                'type': 'geo_shape'
            }
        }
    }
}


class ElasticsearchTileIndex(BaseTileIndex):
    """Elasticsearch TileIndex"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition `dict`

        :returns: `geomet_data_registry.tileindex.elasticsearch_.ElasticsearchTileIndex`  # noqa
        """

        BaseTileIndex.__init__(self, provider_def)

        self.url_parsed = urlparse(self.url)
        self.type_name = 'FeatureCollection'

        LOGGER.debug('Connecting to Elasticsearch')

        if self.url_parsed.path is not None:
            self.es = Elasticsearch(self.url_parsed.netloc,
                                    url_prefix=self.url_parsed.path)
        else:
            self.es = Elasticsearch(self.url_parsed.netloc)

        if not self.es.ping():
            msg = 'Cannot connect to Elasticsearch'
            LOGGER.error(msg)
            raise TileIndexError(msg)

    def setup(self):
        """
        Create the tileindex

        :returns: `bool` of process status
        """

        if self.es.indices.exists(self.name):
            msg = 'Index exists'
            LOGGER.error(msg)
            raise TileIndexError(msg)

        LOGGER.info('Creating index {}'.format(self.name))
        self.es.indices.create(index=self.name, body=INDEX_SETTINGS)
        return True

    def teardown(self):
        """
        Delete the tileindex

        :returns: `bool` of process status
        """

        LOGGER.info('Deleting index {}'.format(self.name))
        try:
            self.es.indices.delete(index=self.name)
        except exceptions.NotFoundError as err:
            msg = err
            LOGGER.error(msg)
            raise TileIndexError(msg)

        return True

    def add(self, identifier, data):
        """
        Add an item to the tileindex

        :param identifier: tileindex item id
        :param data: GeoJSON dict

        :returns: `int` of status (as per HTTP status codes)
        """

        status_code = None

        LOGGER.info('Indexing {}'.format(identifier))
        LOGGER.debug('Data: {}'.format(json_pretty_print(data)))
        try:
            # FIXME: refresh='wait_for' essentially blocks further processing
            # until the document is fully available in ES.  This is done in
            # order to make updates to the layer registration datetime
            # immediately after in support of tracking performance (kind of
            # ironic eh?).
            # TODO: update using asyncio or multiprocessing
            r = self.es.index(index=self.name, id=identifier, body=data,
                              refresh='wait_for')
            if r['result'] == 'created':
                status_code = 201
            elif r['result'] == 'updated':
                status_code = 200
        except Exception as err:
            LOGGER.exception('Error indexing {}: {}'.format(identifier, err))
            return 500

        return status_code

    def update(self, identifier, update_dict):
        """
        Update an existing item in the tileindex

        :param identifier: tileindex item id
        :param data: Python dictionnary

        :returns: `int` of status (as per HTTP status codes)
        """

        LOGGER.info('Updating {}'.format(identifier))

        update_dict = {'doc': update_dict}
        try:
            self.es.update(index=self.name, doc_type=self.type_name,
                           id=identifier, body=update_dict)
        except Exception as err:
            LOGGER.exception('Error updating {}: {}'.format(identifier, err))
            return 500

        return 200

    def update_by_query(self, query_dict, update_dict):
        """
        Update an existing item in the tileindex

        :param identifier: tileindex item id
        :param data: Python dictionnary

        :returns: `int` of status (as per HTTP status codes)
        """

        es_query_body = {}

        LOGGER.info('Updating by query: {}'.format(query_dict))
        LOGGER.info('query dict: {}'.format(query_dict))
        LOGGER.info('update dict: {}'.format(update_dict))

        for key, value in query_dict.items():
            property_name = 'properties.{}.raw'.format(key)
            es_query_body['query'] = {
                'match': {
                    property_name: {
                        'query': value
                    }
                }
            }

        for key, value in update_dict.items():
            es_query_body['script'] = {
                'source': 'ctx._source.properties.{} = "{}"'.format(
                    key, value.isoformat())
            }

        LOGGER.debug('ES query body: {}'.format(es_query_body))
        LOGGER.debug('Updating by query in ES')
        try:
            self.es.update_by_query(index=self.name, body=es_query_body,
                                    conflicts='proceed')
        except Exception as err:
            LOGGER.exception('Error updating by query: {}'.format(err))
            return 500

        return 200

    def __repr__(self):
        return '<ElasticsearchTileIndex> {}'.format(self.url)
