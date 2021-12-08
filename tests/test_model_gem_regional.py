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


class TestModelGemRegionalLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_gem_regional', 'ModelGemRegionalLayer')

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
            'name': 'model_gem_regional',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        model_gem_regional_layer_attr = (
            self.layer_handler['model_gem_regional'].__dict__
        )

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(
            expected_values, model_gem_regional_layer_attr, msg=None
        )

    def test_super_init(self):
        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with(
            {'name': 'model_gem_regional'}
        )


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_gem_regional', 'ModelGemRegionalLayer')

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.model_gem_regional.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        self.check_dependencies_patcher = patch(
            'geomet_data_registry.layer.model_gem_regional.BaseLayer.check_layer_dependencies'  # noqa
        )
        self.mocked_check_dependencies = (
            self.check_dependencies_patcher.start()
        )

        self.config_dependencies_patcher = patch(
            'geomet_data_registry.layer.model_gem_regional.BaseLayer.configure_layer_with_dependencies'  # noqa
        )
        self.mocked_config_dependencies = (
            self.config_dependencies_patcher.start()
        )

        self.is_valid_patcher = patch(
            'geomet_data_registry.layer.model_gem_regional.BaseLayer.is_valid_interval'  # noqa
        )
        self.mocked_valid_interval = self.is_valid_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = {
            'model_gem_regional': {
                'filename_pattern': 'CMC_reg_{wx_variable}_ps10km_{YYYYMMDD_model_run}_P{forecast_hour}.grib2',  # noqa
                'variable': {
                    'ABSV_ISBL_250': {
                        'geomet_layers': {
                            'RDPS.PRES_QQ.250': {
                                'forecast_hours': '000/084/PT1H'
                            }
                        },
                        'elevation': '250mb',
                        'model_run': {'00Z': {'files_expected': '85'}},
                        'members': 'null',
                        'bands_order': ['WDIR_ISBL_225'],
                    }
                },
                'model_run_retention_hours': '48',
                'model_run_interval_hours': '6',
                'dimensions': {'x': '935', 'y': '824'},
            }
        }
        self.mocked_load_plugin.return_value.get_key.side_effect = (
            self.side_effect
        )

        self.filepath = './geomet_data_registry/tests/data/model_gem_regional/grib2/forecast/raw/2020/11/CMC_reg_ABSV_ISBL_250_ps10km_202011220_P001.grib2'  # noqa
        self.layer_handler['model_gem_regional'].filepath = self.filepath

        self.expected_items = [
            {
                'elevation': '250mb',
                'expected_count': '85',
                'filepath': self.filepath,
                'forecast_hour_datetime': '2020-11-22T01:00:00Z',
                'forecast_hours': {'begin': 0, 'end': 84, 'interval': 'PT1H'},
                'identifier': 'RDPS.PRES_QQ.250-20201122000000-20201122010000',
                'layer_config': {'forecast_hours': '000/084/PT1H'},
                'layer_name': 'RDPS.PRES_QQ.250',
                'member': 'null',
                'model': 'model_gem_regional',
                'reference_datetime': '2020-11-22T00:00:00Z',
                'refresh_config': True,
                'register_status': True,
            }
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
        self.assertTrue(
            self.layer_handler['model_gem_regional'].identify(self.filepath)
        )

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify(self):

        # assert you get expected items with the received JSON
        self.layer_handler['model_gem_regional'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_gem_regional'].items
        )

    def test_dependencies_identify(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['model_gem_regional']['variable']['ABSV_ISBL_250']['geomet_layers']['RDPS.PRES_QQ.250']['dependencies'] = ['RDPS.PRES_WSPD.225']  # noqa

        # make self.check_layer_dependencies return False
        self.mocked_check_dependencies.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_gem_regional'].identify(self.filepath)
        )

        # assert these are the only params that changed from expected items
        self.expected_items[0]['register_status'] = False
        self.expected_items[0]['layer_config']['dependencies'] = [
            'RDPS.PRES_WSPD.225'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_gem_regional'].items
        )

    def test_config_dependencies_identify(self):
        # make store.get_key return the JSON string with dependencies
        self.mocked_load_plugin.return_value.get_key.return_value['model_gem_regional']['variable']['ABSV_ISBL_250']['geomet_layers']['RDPS.PRES_QQ.250']['dependencies'] = ['RDPS.PRES_WSPD.225']  # noqa

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
            self.layer_handler['model_gem_regional'].identify(self.filepath)
        )

        # assert these are the only params that changed from self.item
        (
            self.expected_items[0]['filepath'],
            self.expected_items[0]['url'],
            self.expected_items[0]['weather_variable'],
        ) = self.mocked_config_dependencies.return_value
        self.expected_items[0]['register_status'] = True
        self.expected_items[0]['layer_config']['dependencies'] = [
            'RDPS.PRES_WSPD.225'
        ]
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_gem_regional'].items
        )

    def test_invalid_interval_identify(self):
        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_gem_regional'].identify(self.filepath)
        )

        # assert the item is the same as earlier with register_status False
        self.expected_items[0]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_gem_regional'].items
        )

    def test_unsuccessful_identify(self):
        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace(
            'ABSV_ISBL_250', 'Not_wx_variable'
        )
        self.assertFalse(
            self.layer_handler['model_gem_regional'].identify(self.filepath)
        )


if __name__ == '__main__':
    unittest.main()
