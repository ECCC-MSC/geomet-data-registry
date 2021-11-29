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

import json
import unittest
from unittest.mock import patch

from .setup_test_class import Setup


class TestCgslLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'cgsl', 'CgslLayer')

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
            'name': 'cgsl',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        cgsl_layer_attr = self.layer_handler['cgsl'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, cgsl_layer_attr, msg=None)

    def test_super_init(self):
        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'cgsl'})


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'cgsl', 'CgslLayer')

        self.is_valid_patcher = patch(
            'geomet_data_registry.layer.cgsl.BaseLayer.is_valid_interval'
        )
        self.mocked_valid_interval = self.is_valid_patcher.start()

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.cgsl.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'cgsl': {
                    'filename_pattern': 'CMC_coupled-rdps-stlawrence-{wx_variable}_latlon0.02x0.03_{YYYYMMDD_model_run}_P{forecast_hour}.grib2',  # noqa
                    'variable': {
                        'ocean': {
                            'geomet_layers': {
                                'CGSL.ETA_ICEC': {
                                    'bands': '1',
                                    'forecast_hours': '001/048/PT1H',
                                }
                            },
                            'elevation': 'surface',
                            'model_run': {'00Z': {'files_expected': '48'}},
                            'members': 'null',
                            'bands': {'1': {'product': 'ICEC'}},
                        }
                    },
                    'bands': {
                        '1': {'member': '1', 'forecast_interval': 'P0M'}
                    },
                }
            }
        )

        self.filepath = './geomet_data_registry/tests/data/cgsl/grib2/forecast/raw/2020/11/CMC_coupled-rdps-stlawrence-ocean_latlon0.02x0.03_202011220_P001.grib2'  # noqa
        self.layer_handler['cgsl'].filepath = self.filepath

        self.expected_items = [
            {
                'layer_name': 'CGSL.ETA_ICEC',
                'filepath': 'vrt://{}?bands=1'.format(self.filepath),
                'identifier': 'CGSL.ETA_ICEC-20201122000000-20201122010000',
                'reference_datetime': '2020-11-22T00:00:00Z',
                'forecast_hour_datetime': '2020-11-22T01:00:00Z',
                'member': 'null',
                'model': 'cgsl',
                'elevation': 'surface',
                'expected_count': '48',
                'forecast_hours': {'begin': 1, 'end': 48, 'interval': 'PT1H'},
                'layer_config': {
                    'bands': '1',
                    'forecast_hours': '001/048/PT1H',
                },
                'register_status': True,
                'refresh_config': True,
            }
        ]

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

        self.is_valid_patcher.stop()
        self.super_identify_patcher.stop()

    def test_successful_identify(self):
        # assert file was successfully identified
        self.assertTrue(self.layer_handler['cgsl'].identify(self.filepath))

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify(self):
        # assert you get expected items with the received JSON
        self.layer_handler['cgsl'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['cgsl'].items
        )

    def test_invalid_interval_identify(self):
        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['cgsl'].identify(self.filepath))

        # assert the item is the same as earlier with register_status False
        self.expected_items[0]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['cgsl'].items
        )

    def test_unsuccessful_identify(self):
        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace('ocean', 'Not_wx_variable')
        self.assertFalse(self.layer_handler['cgsl'].identify(self.filepath))


if __name__ == '__main__':
    unittest.main()
