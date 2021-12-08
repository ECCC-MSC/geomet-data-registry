###############################################################################
#
# Copyright (C) 2021 Philippe Théroux
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

import unittest
from unittest.mock import patch

from .setup_test_class import Setup


class TestGiopsLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_giops', 'GiopsLayer')

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

    def test_init(self):

        expected_values = {
            'items': [],
            'model_run_list': [],
            'receive_datetime': self.today_date,
            'identify_datetime': None,
            'register_datetime': None,
            'filepath': None,
            'url': None,
            'dimensions': None,
            'model': None,
            'model_run': None,
            'geomet_layers': None,
            'wx_variable': None,
            'date_': None,
            'file_dict': None,
            'new_key_store': False,
            'name': 'model_giops',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
            'dimension': None,
            'bands': None,
        }

        model_giops_layer_attr = self.layer_handler['model_giops'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, model_giops_layer_attr, msg=None)

    def test_super_init(self):
        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'giops'})


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_giops', 'GiopsLayer')

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.model_giops.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        self.check_dependencies_patcher = patch(
            'geomet_data_registry.layer.model_giops.BaseLayer.check_layer_dependencies'  # noqa
        )
        self.mocked_check_dependencies = (
            self.check_dependencies_patcher.start()
        )

        self.config_dependencies_patcher = patch(
            'geomet_data_registry.layer.model_giops.BaseLayer.configure_layer_with_dependencies'  # noqa
        )
        self.mocked_config_dependencies = (
            self.config_dependencies_patcher.start()
        )

        self.is_valid_patcher = patch(
            'geomet_data_registry.layer.model_giops.BaseLayer.is_valid_interval'  # noqa
        )
        self.mocked_valid_interval = self.is_valid_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = {
            'model_giops': {
                'filename_pattern': 'CMC_giops_{wx_variable}_{fileinfo:NonWhitespaceChars}_{YYYYMMDD_model_run}_P{forecast_hour:n}.nc',  # noqa
                '2D': {
                    'variable': {
                        'iiceconc': {
                            'geomet_layers': {
                                'OCEAN.GIOPS.2D_GL': {
                                    'forecast_hours': '003/240/PT3H'
                                }
                            },
                            'elevation': 'surface',
                            'model_run': {'00Z': {'files_expected': '80'}},
                            'members': 'null',
                            'bands_order': ['vozocrtx'],
                        }
                    }
                },
                '3D': {
                    'variable': {
                        'vosaline': {
                            'geomet_layers': {
                                'OCEAN.GIOPS.3D_SALW_{}': {
                                    'forecast_hours': '024/240/PT24H'
                                }
                            },
                            'elevation': 'surface',
                            'model_run': {'00Z': {'files_expected': '10'}},
                            'members': 'null',
                            'bands': {
                                '1': {
                                    'product': '0000',
                                    'elevation': 'surface',
                                }
                            },
                        }
                    }
                },
                'model_run_retention_hours': '120',
                'model_run_interval_hours': '12',
                'dimensions': {'x': '1800', 'y': '850'},
            }
        }
        self.mocked_load_plugin.return_value.get_key.side_effect = (
            self.side_effect
        )

        # filepath and expected items for 2d and 3d
        if '2d' in self.id().split('.')[-1]:
            self.filepath = './geomet_data_registry/tests/data/model_giops/grib2/forecast/2d/2020/11/CMC_giops_iiceconc_notUsedSoWhatever_202011220_P001.nc'  # noqa
            self.expected_items = [
                {
                    'elevation': 'surface',
                    'expected_count': '80',
                    'filepath': self.filepath,
                    'forecast_hour_datetime': '2020-11-22T01:00:00Z',
                    'forecast_hours': {
                        'begin': 3,
                        'end': 240,
                        'interval': 'PT3H',
                    },
                    'identifier': (
                        'OCEAN.GIOPS.2D_GL-20201122000000-20201122010000'
                    ),
                    'layer_config': {'forecast_hours': '003/240/PT3H'},
                    'layer_name': 'OCEAN.GIOPS.2D_GL',
                    'member': 'null',
                    'model': 'model_giops_2D',
                    'reference_datetime': '2020-11-22T00:00:00Z',
                    'refresh_config': True,
                    'register_status': True,
                }
            ]
        else:
            self.filepath = './geomet_data_registry/tests/data/model_giops/grib2/forecast/3d/2020/11/CMC_giops_vosaline_notUsedSoWhatever_202011220_P001.nc'  # noqa
            self.expected_items = [
                {
                    'elevation': 'surface',
                    'expected_count': '10',
                    'filepath': self.filepath,
                    'forecast_hour_datetime': '2020-11-22T01:00:00Z',
                    'forecast_hours': {
                        'begin': 24,
                        'end': 240,
                        'interval': 'PT24H',
                    },
                    'identifier': (
                        'OCEAN.GIOPS.3D_SALW_0000-20201122000000-20201122010000'  # noqa
                    ),
                    'layer_config': {'forecast_hours': '024/240/PT24H'},
                    'layer_name': 'OCEAN.GIOPS.3D_SALW_0000',
                    'layer_name_unformatted': 'OCEAN.GIOPS.3D_SALW_{}',
                    'member': None,
                    'model': 'model_giops_3D',
                    'reference_datetime': '2020-11-22T00:00:00Z',
                    'refresh_config': True,
                    'register_status': True,
                }
            ]

        self.layer_handler['model_giops'].filepath = self.filepath

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

        self.super_identify_patcher.stop()
        self.check_dependencies_patcher.stop()
        self.config_dependencies_patcher.stop()
        self.is_valid_patcher.stop()

    def test_successful_identify2d(self):

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_giops'].identify(self.filepath)
        )

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify2d(self):

        # assert you get expected items with the received JSON
        self.layer_handler['model_giops'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_giops'].items
        )

    def test_dependencies_identify2d(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['model_giops']['2D']['variable']['iiceconc']['geomet_layers']['OCEAN.GIOPS.2D_GL']['dependencies'] = ['OCEAN.GIOPS.2D.UUX']  # noqa

        # make self.check_layer_dependencies return False
        self.mocked_check_dependencies.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_giops'].identify(self.filepath)
        )

        # assert these are the only params that changed from expected items
        self.expected_items[0]['register_status'] = False
        self.expected_items[0]['layer_config']['dependencies'] = [
            'OCEAN.GIOPS.2D.UUX'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_giops'].items
        )

    def test_config_dependencies_identify2d(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['model_giops']['2D']['variable']['iiceconc']['geomet_layers']['OCEAN.GIOPS.2D_GL']['dependencies'] = ['OCEAN.GIOPS.2D.UUX']  # noqa

        # make self.check_layer_dependencies return True
        self.mocked_check_dependencies.return_value = True

        # make self.configure_layer_with_dependencies return this list
        self.mocked_config_dependencies.return_value = [
            'vrt',
            'urls',
            'weather_variables',
        ]

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_giops'].identify(self.filepath)
        )

        # assert these are the only params that changed from expected items
        (
            self.expected_items[0]['filepath'],
            self.expected_items[0]['url'],
            self.expected_items[0]['weather_variable'],
        ) = self.mocked_config_dependencies.return_value
        self.expected_items[0]['register_status'] = True
        self.expected_items[0]['layer_config']['dependencies'] = [
            'OCEAN.GIOPS.2D.UUX'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_giops'].items
        )

    def test_invalid_interval_identify2d(self):
        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_giops'].identify(self.filepath)
        )

        # assert the item is the same as earlier with register_status False
        self.expected_items[0]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_giops'].items
        )

    def test_unsuccessful_identify2d(self):
        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace('iiceconc', 'Not_wx_variable')
        self.assertFalse(
            self.layer_handler['model_giops'].identify(self.filepath)
        )

    def test_successful_identify3d(self):

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_giops'].identify(self.filepath)
        )

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify3d(self):

        # assert you get expected items with the received JSON
        self.layer_handler['model_giops'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_giops'].items
        )

    def test_dependencies_identify3d(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['model_giops']['3D']['variable']['vosaline']['geomet_layers']['OCEAN.GIOPS.3D_SALW_{}']['dependencies'] = ['OCEAN.GIOPS.3D_UU2W_Y_{}']  # noqa

        # make self.check_layer_dependencies return False
        self.mocked_check_dependencies.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_giops'].identify(self.filepath)
        )

        # assert these are the only params that changed from expected items
        self.expected_items[0]['register_status'] = False
        self.expected_items[0]['layer_config']['dependencies'] = [
            'OCEAN.GIOPS.3D_UU2W_Y_0000'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_giops'].items
        )

    def test_config_dependencies_identify3d(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['model_giops']['3D']['variable']['vosaline']['geomet_layers']['OCEAN.GIOPS.3D_SALW_{}']['dependencies'] = ['OCEAN.GIOPS.3D_UU2W_Y_{}']  # noqa

        # make self.check_layer_dependencies return True
        self.mocked_check_dependencies.return_value = True

        # make self.configure_layer_with_dependencies return this list
        self.mocked_config_dependencies.return_value = [
            'vrt',
            'urls',
            'weather_variables',
        ]

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_giops'].identify(self.filepath)
        )

        # assert these are the only params that changed from expected items
        (
            self.expected_items[0]['filepath'],
            self.expected_items[0]['url'],
            self.expected_items[0]['weather_variable'],
        ) = self.mocked_config_dependencies.return_value
        self.expected_items[0]['register_status'] = True
        self.expected_items[0]['layer_config']['dependencies'] = [
            'OCEAN.GIOPS.3D_UU2W_Y_0000'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_giops'].items
        )

    def test_invalid_interval_identify3d(self):
        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_giops'].identify(self.filepath)
        )

        # assert the item is the same as earlier with register_status False
        self.expected_items[0]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_giops'].items
        )

    def test_unsuccessful_identify3d(self):
        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace('vosaline', 'Not wx_variable')
        self.assertFalse(
            self.layer_handler['model_giops'].identify(self.filepath)
        )


if __name__ == '__main__':
    unittest.main()
