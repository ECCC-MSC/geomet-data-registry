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

from geomet_data_registry.tileindex.base import (
    BaseTileIndex,
    TileIndexError,
    TileNotFoundError,
)
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
                    'url': {
                        'type': 'text',
                        'fields': {
                            'raw': {
                                'type': 'keyword'
                            }
                        }
                    },
                    'forecast_hour_datetime': {
                        'type': 'date',
                        'format': 'date_time_no_millis'
                    },
                    'reference_datetime': {
                        'type': 'date',
                        'format': 'date_time_no_millis'
                    },
                    'receive_datetime': {
                        'type': 'date',
                        'format': 'date_time'
                    },
                    'identify_datetime': {
                        'type': 'date',
                        'format': 'date_time'
                    },
                    'register_datetime': {
                        'type': 'date',
                        'format': 'date_time'
                    },
                    'expiry_datetime': {
                        'type': 'date',
                        'format': 'date_time'
                    },
                    'elevation': {
                        'type': 'text',
                        'fields': {
                            'raw': {
                                'type': 'keyword'
                            }
                         }
                    },
                    'model': {
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

        super().__init__(provider_def)

        self.url_parsed = urlparse(self.url)
        self.type_name = 'FeatureCollection'

        LOGGER.debug('Connecting to Elasticsearch')

        if self.url_parsed.port is None:  # proxy to default HTTP(S) port
            if self.url_parsed.scheme == 'https':
                port = 443
            else:
                port = 80
        else:  # was set explictly
            port = self.url_parsed.port

        url_settings = {
            'host': self.url_parsed.hostname,
            'port': port
        }

        if self.url_parsed.path:
            url_settings['url_prefix'] = self.url_parsed.path

        LOGGER.debug('URL settings: {}'.format(url_settings))

        self.es = Elasticsearch([url_settings])

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
        self.es.ingest.put_pipeline(id='gdr_register_datetime', body={
            'description': 'Adds a timestamp to a geomet-data-registry '
                           'document\'s properties.register_datetime property '
                           'as the document is indexed.',
            'processors': [
                {
                    'set': {
                        'field': 'properties.register_datetime',
                        'value': '{{_ingest.timestamp}}'
                    }
                }
            ]
        })

        return True

    def teardown(self):
        """
        Delete the tileindex

        :returns: `bool` of process status
        """

        LOGGER.info('Deleting index {}'.format(self.name))
        try:
            self.es.indices.delete(index=self.name)
            self.es.ingest.delete_pipeline(id='gdr_register_datetime')
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
                              pipeline='gdr_register_datetime')
            if r['result'] == 'created':
                status_code = 201
            elif r['result'] == 'updated':
                status_code = 200
        except Exception as err:
            LOGGER.exception('Error indexing {}: {}'.format(identifier, err))
            return 500

        return status_code

    def bulk_add(self, data):
        """
        Add many items to the tileindex

        :param data: GeoJSON dict

        :returns: `dict` {layer_id: HTTP status code}
        """

        LOGGER.debug('Starting bulk add')
        try:
            # until the document is fully available in ES.  This is done in
            # order to make updates to the layer registration datetime
            # immediately after in support of tracking performance (kind of
            # ironic eh?).
            # TODO: update using asyncio or multiprocessing

            # add 'pipeline': 'register_datetime' to data_es
            bulk_data = []
            for doc in data:
                op_dict = {
                    'index': {
                        '_index': self.name,
                        '_type': '_doc'
                    }
                }
                op_dict['index']['_id'] = doc['properties']['identifier']
                bulk_data.append(op_dict)
                bulk_data.append(doc)
            r = self.es.bulk(index=self.name, body=bulk_data,
                             pipeline='gdr_register_datetime')

            status_dict = {}

            for i in r['items']:
                lyr_id = i['index']['_id']
                lyr_status = i['index']['status']
                tmp_dict = {}
                tmp_dict[lyr_id] = lyr_status
                status_dict.update(tmp_dict)

        except Exception as err:
            LOGGER.exception('Error bulk indexing: {}'.format(err))
            return 500

        return status_dict

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
                'wildcard': {
                    property_name: {
                        'wildcard': value
                    }
                }
            }

        for key, value in update_dict.items():
            es_query_body['script'] = {
                'source': 'ctx._source.properties.{} = "{}"'.format(
                    key, value)
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

    def get(self, identifier):
        """
        :param identifier: identifier of document to retrieve
        :returns: `dict` of single GeoJSON feature
        """
        try:
            result = self.es.get(index=self.name, id=identifier)
            return result['_source']
        except exceptions.NotFoundError as err:
            LOGGER.warning('Could not get document with id: {}'.format(err))
            raise TileNotFoundError()

    def __repr__(self):
        return '<ElasticsearchTileIndex> {}'.format(self.url)
