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


class TestRiopsLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_riops', 'RiopsLayer')

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
            'name': 'model_riops',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
            'dimension': None,
            'bands': None,
        }

        model_riops_layer_attr = self.layer_handler['model_riops'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, model_riops_layer_attr, msg=None)

    def test_super_init(self):
        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'riops'})

    def test_repr(self):
        self.assertEqual(
            repr(self.layer_handler['model_riops']),
            '<ModelRiopsLayer> model_riops'
        )


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_riops', 'RiopsLayer')

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.model_riops.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        self.check_dependencies_patcher = patch(
            'geomet_data_registry.layer.model_riops.BaseLayer.check_layer_dependencies'  # noqa
        )
        self.mocked_check_dependencies = (
            self.check_dependencies_patcher.start()
        )

        self.config_dependencies_patcher = patch(
            'geomet_data_registry.layer.model_riops.BaseLayer.configure_layer_with_dependencies'  # noqa
        )
        self.mocked_config_dependencies = (
            self.config_dependencies_patcher.start()
        )

        self.is_valid_patcher = patch(
            'geomet_data_registry.layer.model_riops.BaseLayer.is_valid_interval'  # noqa
        )
        self.mocked_valid_interval = self.is_valid_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = {
            'model_riops': {
                'filename_pattern': '{YYYYMMDD_model_run}_MSC_RIOPS_{wx_variable}_{elevation}_PS5km_P{forecast_hour:n}.nc',  # noqa
                '2D': {
                    'variable': {
                        'IICECONC': {
                            'geomet_layers': {
                                'RIOPS_IICECONC_SFC': {
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
                        'VOMECRTY': {
                            'geomet_layers': {
                                'RIOPS_UU2W_Y_DBS-{}': {
                                    'forecast_hours': '000/048/PT1H'
                                }
                            },
                            'model_run': {'00Z': {'files_expected': '49'}},
                            'members': 'null',
                            'bands': {
                                '2': {
                                    'product': '1.6m',
                                    'elevation': '-1.6m',
                                }
                            },
                            'bands_order': ['VOZOCRTX'],
                        }
                    }
                },
                'model_run_retention_hours': '96',
                'model_run_interval_hours': '6',
                'dimensions': {'x': '1770', 'y': '1610'},
            }
        }
        self.mocked_load_plugin.return_value.get_key.side_effect = (
            self.side_effect
        )

        # filepath and received items for 2d and 3d
        if '2d' in self.id().split('.')[-1]:
            self.filepath = './geomet_data_registry/tests/data/model_riops/grib2/forecast/2d/2020/11/20201122T0Z_MSC_RIOPS_IICECONC_surface_PS5km_P003.nc'  # noqa
            self.expected_items = [
                {
                    'elevation': 'surface',
                    'expected_count': '80',
                    'filepath': self.filepath,
                    'forecast_hour_datetime': '2020-11-22T03:00:00Z',
                    'forecast_hours': {
                        'begin': 3,
                        'end': 240,
                        'interval': 'PT3H',
                    },
                    'identifier': (
                        'RIOPS_IICECONC_SFC-20201122000000-20201122030000'
                    ),
                    'layer_config': {'forecast_hours': '003/240/PT3H'},
                    'layer_name': 'RIOPS_IICECONC_SFC',
                    'member': 'null',
                    'model': 'model_riops_2D',
                    'reference_datetime': '2020-11-22T00:00:00Z',
                    'register_status': True,
                }
            ]
        else:
            self.filepath = './geomet_data_registry/tests/data/model_riops/grib2/forecast/3d/2020/11/20201122T0Z_MSC_RIOPS_VOMECRTY_-1.6m_PS5km_P000.nc'  # noqa
            self.expected_items = [
                {
                    'elevation': '-1.6m',
                    'expected_count': '49',
                    'filepath': self.filepath,
                    'forecast_hour_datetime': '2020-11-22T00:00:00Z',
                    'forecast_hours': {
                        'begin': 0,
                        'end': 48,
                        'interval': 'PT1H',
                    },
                    'identifier': (
                        'RIOPS_UU2W_Y_DBS-1.6m-20201122000000-20201122000000'
                    ),
                    'layer_config': {'forecast_hours': '000/048/PT1H'},
                    'layer_name': 'RIOPS_UU2W_Y_DBS-1.6m',
                    'layer_name_unformatted': 'RIOPS_UU2W_Y_DBS-{}',
                    'member': None,
                    'model': 'model_riops_3D',
                    'reference_datetime': '2020-11-22T00:00:00Z',
                    'register_status': True,
                }
            ]

        self.layer_handler['model_riops'].filepath = self.filepath

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
            self.layer_handler['model_riops'].identify(self.filepath)
        )

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify2d(self):

        # assert you get expected items with the received JSON
        self.layer_handler['model_riops'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_riops'].items
        )

    def test_dependencies_identify2d(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['model_riops']['2D']['variable']['IICECONC']['geomet_layers']['RIOPS_IICECONC_SFC']['dependencies'] = ['RIOPS_UUX_SFC']  # noqa

        # make self.check_layer_dependencies return False
        self.mocked_check_dependencies.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_riops'].identify(self.filepath)
        )

        # assert these are the only params that changed from expected items
        self.expected_items[0]['register_status'] = False
        self.expected_items[0]['layer_config']['dependencies'] = [
            'RIOPS_UUX_SFC'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_riops'].items
        )

    def test_config_dependencies_identify2d(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['model_riops']['2D']['variable']['IICECONC']['geomet_layers']['RIOPS_IICECONC_SFC']['dependencies'] = ['RIOPS_UUX_SFC']  # noqa

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
            self.layer_handler['model_riops'].identify(self.filepath)
        )

        # assert these are the only params that changed from expected items
        (
            self.expected_items[0]['filepath'],
            self.expected_items[0]['url'],
            self.expected_items[0]['weather_variable'],
        ) = self.mocked_config_dependencies.return_value
        self.expected_items[0]['register_status'] = True
        self.expected_items[0]['layer_config']['dependencies'] = [
            'RIOPS_UUX_SFC'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_riops'].items
        )

    def test_invalid_interval_identify2d(self):
        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_riops'].identify(self.filepath)
        )

        # assert the item is the same as earlier with register_status False
        self.expected_items[0]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_riops'].items
        )

    def test_unsuccessful_identify2d(self):
        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace('IICECONC', 'Not_wx_variable')
        with self.assertLogs(
            'geomet_data_registry.layer.model_riops', level='WARNING'
        ) as warn:
            self.assertFalse(
                self.layer_handler['model_riops'].identify(self.filepath)
            )
            # assert a single LOGGER.warning was called
            self.assertEqual(len(warn.records), 1)

    def test_successful_identify3d(self):

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_riops'].identify(self.filepath)
        )

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify3d(self):

        # assert you get expected items with the received JSON
        self.layer_handler['model_riops'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_riops'].items
        )

    def test_dependencies_identify3d(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['model_riops']['3D']['variable']['VOMECRTY']['geomet_layers']['RIOPS_UU2W_Y_DBS-{}']['dependencies'] = ['RIOPS_UU2W_X_DBS-{}']  # noqa

        # make self.check_layer_dependencies return False
        self.mocked_check_dependencies.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_riops'].identify(self.filepath)
        )

        # assert these are the only params that changed from self.item
        self.expected_items[0]['register_status'] = False
        self.expected_items[0]['layer_config']['dependencies'] = [
            'RIOPS_UU2W_X_DBS-1.6m'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_riops'].items
        )

    def test_config_dependencies_identify3d(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['model_riops']['3D']['variable']['VOMECRTY']['geomet_layers']['RIOPS_UU2W_Y_DBS-{}']['dependencies'] = ['RIOPS_UU2W_X_DBS-{}']  # noqa

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
            self.layer_handler['model_riops'].identify(self.filepath)
        )

        # assert these are the only params that changed from expected items
        (
            self.expected_items[0]['filepath'],
            self.expected_items[0]['url'],
            self.expected_items[0]['weather_variable'],
        ) = self.mocked_config_dependencies.return_value
        self.expected_items[0]['register_status'] = True
        self.expected_items[0]['layer_config']['dependencies'] = [
            'RIOPS_UU2W_X_DBS-1.6m'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_riops'].items
        )

    def test_invalid_interval_identify3d(self):
        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_riops'].identify(self.filepath)
        )

        # assert the item is the same as earlier with register_status False
        self.expected_items[0]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_riops'].items
        )

    def test_unsuccessful_identify3d(self):
        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace('VOMECRTY', 'Not_wx_variable')
        with self.assertLogs(
            'geomet_data_registry.layer.model_riops', level='WARNING'
        ) as warn:
            self.assertFalse(
                self.layer_handler['model_riops'].identify(self.filepath)
            )
            # assert a single LOGGER.warning was called
            self.assertEqual(len(warn.records), 1)


if __name__ == '__main__':
    unittest.main()
