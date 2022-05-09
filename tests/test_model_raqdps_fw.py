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


class TestModelRaqdpsFwLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(
            self, 'model_raqdps_fw', 'ModelRaqdpsFwLayer', 'model_raqdps-fw'
        )

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
            'name': 'model_raqdps-fw',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        model_raqdps_fw_layer_attr = (
            self.layer_handler['model_raqdps_fw'].__dict__
        )

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(
            expected_values, model_raqdps_fw_layer_attr, msg=None
        )

    def test_super_init(self):

        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'model_raqdps-fw'})

    def test_repr(self):
        self.assertEqual(
            repr(self.layer_handler['model_raqdps_fw']),
            '<ModelRaqdpsFwLayer> model_raqdps-fw'
        )


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(
            self, 'model_raqdps_fw', 'ModelRaqdpsFwLayer', 'model_raqdps-fw'
        )

        self.is_valid_patcher = patch(
            'geomet_data_registry.layer.model_raqdps_fw.BaseLayer.is_valid_interval'  # noqa
        )
        self.mocked_valid_interval = self.is_valid_patcher.start()

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.model_raqdps_fw.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'model_raqdps-fw': {
                    'filename_pattern': '{YYYYMMDD}T{model_run}Z_MSC_RAQDPS-FW_{wx_variable}_RLatLon0.09_PT{forecast_hour}H.grib2',  # noqa
                    'variable': {
                        'PM2.5_EAtm': {
                            'geomet_layers': {
                                'RAQDPS-FW.EATM_PM2.5': {
                                    'forecast_hours': '000/072/PT1H'
                                }
                            },
                            'elevation': 'null',
                            'model_run': {'00Z': {'files_expected': '73'}},
                            'members': 'null',
                        }
                    },
                    'dimensions': {'x': '729', 'y': '599'},
                    'model_run_retention_hours': '48',
                    'model_run_interval_hours': '12',
                }
            }
        )

        self.filepath = './geomet_data_registry/tests/data/model_raqdps-fw/10km/grib2/00/000/20211129T00Z_MSC_RAQDPS-FW_PM2.5_EAtm_RLatLon0.09_PT000H.grib2'  # noqa
        self.layer_handler['model_raqdps_fw'].filepath = self.filepath

        self.expected_items = [
            {
                'elevation': 'null',
                'expected_count': '73',
                'filepath': self.filepath,
                'forecast_hour_datetime': '2021-11-29T00:00:00Z',
                'forecast_hours': {'begin': 0, 'end': 72, 'interval': 'PT1H'},
                'identifier': (
                    'RAQDPS-FW.EATM_PM2.5-20211129000000-20211129000000'),
                'layer_config': {'forecast_hours': '000/072/PT1H'},
                'layer_name': 'RAQDPS-FW.EATM_PM2.5',
                'member': 'null',
                'model': 'model_raqdps-fw',
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

        self.is_valid_patcher.stop()
        self.super_identify_patcher.stop()

    def test_successful_identify(self):

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_raqdps_fw'].identify(self.filepath)
        )

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify(self):

        # assert you get expected items with the received JSON
        self.layer_handler['model_raqdps_fw'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_raqdps_fw'].items
        )

    def test_invalidInterval_identify(self):

        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_raqdps_fw'].identify(self.filepath)
        )

        # assert the item is the same as earlier with register_status False
        self.expected_items[0]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['model_raqdps_fw'].items
        )

    def test_unsuccessful_identify(self):
        # assert identify returns False when the wx_variable
        # isn't correct and a warning is logged.
        self.filepath = self.filepath.replace('PM2.5_EAtm', 'Not_wx_variable')
        with self.assertLogs(
            'geomet_data_registry.layer.model_raqdps_fw', level='WARNING'
        ) as warn:
            self.assertFalse(
                self.layer_handler['model_raqdps_fw'].identify(self.filepath)
            )
            # assert a single LOGGER.warning was called
            self.assertEqual(len(warn.records), 1)


if __name__ == '__main__':
    unittest.main()
