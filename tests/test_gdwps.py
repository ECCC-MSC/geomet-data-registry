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


class TestGdwpsLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'gdwps', 'GdwpsLayer')

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
            'name': 'gdwps',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        gdwps_layer_attr = self.layer_handler['gdwps'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, gdwps_layer_attr, msg=None)

    def test_super_init(self):
        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'gdwps'})

    def test_repr(self):
        self.assertEqual(
            repr(self.layer_handler['gdwps']),
            '<ModelGdwpsLayer> gdwps'
        )


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'gdwps', 'GdwpsLayer')

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.gdwps.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        self.check_dependencies_patcher = patch(
            'geomet_data_registry.layer.gdwps.BaseLayer.check_layer_dependencies'  # noqa
        )
        self.mocked_check_dependencies = (
            self.check_dependencies_patcher.start()
        )

        self.config_dependencies_patcher = patch(
            'geomet_data_registry.layer.gdwps.BaseLayer.configure_layer_with_dependencies'  # noqa
        )
        self.mocked_config_dependencies = (
            self.config_dependencies_patcher.start()
        )

        self.is_valid_patcher = patch(
            'geomet_data_registry.layer.gdwps.BaseLayer.is_valid_interval'
        )
        self.mocked_valid_interval = self.is_valid_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = {
            'gdwps': {
                'filename_pattern': '{YYYYMMDD}T{model_run}Z_MSC_GDWPS_{wx_variable}_LatLon0.25_PT{forecast_hour}H.grib2',  # noqa
                'model_run_retention_hours': '48',
                'model_run_interval_hours': '12',
                'dimensions': {'x': '1440', 'y': '721'},
                'variable': {
                    'HTSGW_Sfc': {
                        'geomet_layers': {
                            'GDWPS_25km_HTSGW_PT1H': {
                                'forecast_hours': '000/048/PT1H'
                            },
                            'GDWPS_25km_HTSGW_PT3H': {
                                'forecast_hours': '000/120/PT3H'
                            },
                        },
                        'elevation': 'surface',
                        'model_run': {'00Z': {'files_expected': '73'}},
                        'members': 'null',
                    }
                },
            }
        }
        self.mocked_load_plugin.return_value.get_key.side_effect = (
            self.side_effect
        )

        self.filepath = './geomet_data_registry/tests/data/model_gdwps/00/20211007T00Z_MSC_GDWPS_HTSGW_Sfc_LatLon0.25_PT000H.grib2'  # noqa
        self.layer_handler['gdwps'].filepath = self.filepath

        self.expected_items = [
            {
                'layer_name': 'GDWPS_25km_HTSGW_PT1H',
                'filepath': self.filepath,
                'identifier': 'GDWPS_25km_HTSGW_PT1H-20211007000000-20211007000000',  # noqa
                'reference_datetime': '2021-10-07T00:00:00Z',
                'forecast_hour_datetime': '2021-10-07T00:00:00Z',
                'member': 'null',
                'model': 'gdwps',
                'elevation': 'surface',
                'expected_count': '73',
                'forecast_hours': {'begin': 0, 'end': 48, 'interval': 'PT1H'},
                'layer_config': {'forecast_hours': '000/048/PT1H'},
                'register_status': True,
                'refresh_config': True,
            },
            {
                'layer_name': 'GDWPS_25km_HTSGW_PT3H',
                'filepath': self.filepath,
                'identifier': 'GDWPS_25km_HTSGW_PT3H-20211007000000-20211007000000',  # noqa
                'reference_datetime': '2021-10-07T00:00:00Z',
                'forecast_hour_datetime': '2021-10-07T00:00:00Z',
                'member': 'null',
                'model': 'gdwps',
                'elevation': 'surface',
                'expected_count': '73',
                'forecast_hours': {'begin': 0, 'end': 120, 'interval': 'PT3H'},
                'layer_config': {'forecast_hours': '000/120/PT3H'},
                'register_status': True,
                'refresh_config': True,
            },
        ]

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

        self.super_identify_patcher.stop()
        self.check_dependencies_patcher.stop()
        self.config_dependencies_patcher.stop()
        self.is_valid_patcher.stop()

    def test_successful_identify(self):

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['gdwps'].identify(self.filepath))

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify(self):

        # assert you get self.items with the received JSON
        self.layer_handler['gdwps'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['gdwps'].items
        )

    def test_dependencies_identify(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['gdwps']['variable']['HTSGW_Sfc']['geomet_layers']['GDWPS_25km_HTSGW_PT1H']['dependencies'] = ['GDWPS_25km_HTSGW_PT3H']  # noqa

        # make self.check_layer_dependencies return False
        self.mocked_check_dependencies.return_value = False

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['gdwps'].identify(self.filepath))

        # assert these are the only params that changed from self.items
        self.expected_items[0]['register_status'] = False
        self.expected_items[0]['layer_config']['dependencies'] = [
            'GDWPS_25km_HTSGW_PT3H'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['gdwps'].items
        )

    def test_config_dependencies_identify(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['gdwps']['variable']['HTSGW_Sfc']['geomet_layers']['GDWPS_25km_HTSGW_PT1H']['dependencies'] = ['GDWPS_25km_HTSGW_PT3H']  # noqa

        # make self.check_layer_dependencies return True
        self.mocked_check_dependencies.return_value = True

        # make self.configure_layer_with_dependencies return this list
        self.mocked_config_dependencies.return_value = [
            'vrt',
            'urls',
            'weather_variables',
        ]

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['gdwps'].identify(self.filepath))

        # assert these are the only params that changed from self.item
        (
            self.expected_items[0]['filepath'],
            self.expected_items[0]['url'],
            self.expected_items[0]['weather_variable'],
        ) = self.mocked_config_dependencies.return_value

        self.expected_items[0]['register_status'] = True
        self.expected_items[0]['layer_config']['dependencies'] = [
            'GDWPS_25km_HTSGW_PT3H'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['gdwps'].items
        )

    def test_invalid_interval_identify(self):
        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['gdwps'].identify(self.filepath))

        # assert the items are the same as earlier with register_status False
        self.expected_items[0]['register_status'] = False
        self.expected_items[1]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['gdwps'].items
        )

    def test_unsuccessful_identify(self):
        # assert identify returns False when the wx_variable
        # isn't correct and a warning is logged.
        self.filepath = self.filepath.replace('HTSGW_Sfc', 'Not_wx_variable')
        with self.assertLogs(
            'geomet_data_registry.layer.gdwps', level='WARNING'
        ) as warn:
            self.assertFalse(
                self.layer_handler['gdwps'].identify(self.filepath)
            )
            # assert a single LOGGER.warning was called
            self.assertEqual(len(warn.records), 1)


if __name__ == '__main__':
    unittest.main()
