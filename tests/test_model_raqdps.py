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


class TestModelRaqdpsLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_raqdps', 'ModelRaqdpsLayer')

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
            'name': 'model_raqdps',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        model_raqdps_layer_attr = self.layer_handler['model_raqdps'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(
            expected_values, model_raqdps_layer_attr, msg=None
        )

    def test_super_init(self):
        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'model_raqdps'})


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_raqdps', 'ModelRaqdpsLayer')

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.model_raqdps.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        self.is_valid_patcher = patch(
            'geomet_data_registry.layer.model_raqdps.BaseLayer.is_valid_interval'  # noqa
        )
        self.mocked_valid_interval = self.is_valid_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'model_raqdps': {
                    'filename_pattern': '{YYYYMMDD}T{model_run}Z_MSC_RAQDPS_{wx_variable}_RLatLon0.09_PT{forecast_hour}H.grib2',  # noqa
                    'variable': {
                        'PM2.5_EAtm': {
                            'geomet_layers': {
                                'RAQDPS.EATM_PM2.5': {
                                    'forecast_hours': '000/072/PT1H'
                                }
                            },
                            'elevation': 'null',
                            'model_run': {'00Z': {'files_expected': '73'}},
                            'members': 'null',
                        }
                    },
                    'model_run_retention_hours': '48',
                    'model_run_interval_hours': '12',
                    'dimensions': {'x': '2400', 'y': '1201'},
                }
            }
        )

        self.filepath = './geomet_data_registry/tests/data/model_raqdps/10km/grib2/00/000/20211129T00Z_MSC_RAQDPS_PM2.5_EAtm_RLatLon0.09_PT000H.grib2'  # noqa
        self.layer_handler['model_raqdps'].filepath = self.filepath

        self.expected_items = [
            {
                'elevation': 'null',
                'expected_count': '73',
                'filepath': self.filepath,
                'forecast_hour_datetime': '2021-11-29T00:00:00Z',
                'forecast_hours': {'begin': 0, 'end': 72, 'interval': 'PT1H'},
                'identifier': (
                    'RAQDPS.EATM_PM2.5-20211129000000-20211129000000'
                ),
                'layer_config': {'forecast_hours': '000/072/PT1H'},
                'layer_name': 'RAQDPS.EATM_PM2.5',
                'member': 'null',
                'model': 'model_raqdps',
                'reference_datetime': '2021-11-29T00:00:00Z',
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
        self.is_valid_patcher.stop()

    def test_successful_identify(self):

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_raqdps'].identify(self.filepath)
        )

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify(self):

        # assert you get expected items with the received JSON
        self.layer_handler['model_raqdps'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_raqdps'].items
        )

    def test_invalid_interval_identify(self):
        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_raqdps'].identify(self.filepath)
        )

        # assert the item is the same as earlier with register_status False
        self.expected_items[0]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_raqdps'].items
        )

    def test_unsuccessful_identify(self):
        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace('PM2.5_EAtm', 'Not_wx_variable')
        self.assertFalse(
            self.layer_handler['model_raqdps'].identify(self.filepath)
        )


if __name__ == '__main__':
    unittest.main()
