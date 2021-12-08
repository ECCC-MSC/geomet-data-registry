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


class TestRepsLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'reps', 'RepsLayer')

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
            'name': 'reps',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
            'type': None,
            'bands': None,
        }

        reps_layer_attr = self.layer_handler['reps'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, reps_layer_attr, msg=None)

    def test_super_init(self):
        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'reps'})


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'reps', 'RepsLayer')

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.reps.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        self.is_valid_patcher = patch(
            'geomet_data_registry.layer.reps.BaseLayer.is_valid_interval'
        )
        self.mocked_valid_interval = self.is_valid_patcher.start()

        self.filepath = './geomet_data_registry/tests/reps/grib2/forecast/raw/2020/11/CMC-reps-srpe-prob_TPRATE-Accum-3h_SFC_0_ps15km_202011220_P03_all-products.grib2'  # noqa
        self.layer_handler['reps'].filepath = self.filepath

        # make store.get_key return this JSON string (product)
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'reps': {
                    'product': {
                        'filename_pattern': 'CMC-reps-srpe-prob_{wx_variable}_ps15km_{YYYYMMDD_model_run}_P{forecast_hour}_all-products.grib2',  # noqa
                        'variable': {
                            'TPRATE-Accum-3h_SFC_0': {
                                'geomet_layers': {
                                    'REPS.DIAG.3_PRMM.{}': {
                                        'forecast_hours': '03/72/PT3H'
                                    }
                                },
                                'bands': {'1': {'product': 'ERGE1'}},
                                'elevation': 'surface',
                                'model_run': {'00Z': {'files_expected': '24'}},
                                'members': 'null',
                            }
                        },
                    },
                    'model_run_retention_hours': '48',
                    'model_run_interval_hours': '6',
                }
            }
        )

        self.expected_items = [
            {
                'elevation': 'surface',
                'expected_count': '24',
                'filepath': 'vrt://{}?bands=1'.format(self.filepath),
                'forecast_hour_datetime': '2020-11-22T03:00:00Z',
                'forecast_hours': {'begin': 3, 'end': 72, 'interval': 'PT3H'},
                'identifier': (
                    'REPS.DIAG.3_PRMM.ERGE1-20201122000000-20201122030000'
                ),
                'layer_config': {'forecast_hours': '03/72/PT3H'},
                'layer_name': 'REPS.DIAG.3_PRMM.ERGE1',
                'layer_name_unformatted': 'REPS.DIAG.3_PRMM.{}',
                'member': None,
                'model': 'reps',
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
        self.is_valid_patcher.stop()

    def test_successful_identify(self):
        # assert file was successfully identified
        self.assertTrue(self.layer_handler['reps'].identify(self.filepath))

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_product_identify(self):
        # assert you get expected items with the received JSON
        self.layer_handler['reps'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['reps'].items
        )

    def test_member_identify(self):
        # make store.get_key return this JSON string (member)
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'reps': {
                    'member': {
                        'filename_pattern': 'CMC-reps-srpe-raw_{wx_variable}_ps15km_{YYYYMMDD_model_run}_P{forecast_hour}_allmbrs.grib2',  # noqa
                        'variable': {
                            'PRMSL_MSL_0': {
                                'geomet_layers': {
                                    'REPS.MEM.ETA_PN.{}': {
                                        'forecast_hours': '00/72/PT3H'
                                    }
                                },
                                'elevation': 'surface',
                                'model_run': {'00Z': {'files_expected': '25'}},
                                'members': '1',
                            }
                        },
                        'bands': {'1': {'member': '1'}},
                    },
                    'model_run_retention_hours': '48',
                    'model_run_interval_hours': '6',
                }
            }
        )
        filepath = './geomet_data_registry/tests/reps/grib2/forecast/raw/2020/11/CMC-reps-srpe-raw_PRMSL_MSL_0_ps15km_202011220_P00_allmbrs.grib2'  # noqa
        self.layer_handler['reps'].filepath = filepath

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['reps'].identify(filepath))

        expected_items = [
            {
                'elevation': 'surface',
                'expected_count': '25',
                'filepath': 'vrt://{}?bands=1'.format(filepath),
                'forecast_hour_datetime': '2020-11-22T00:00:00Z',
                'forecast_hours': {'begin': 0, 'end': 72, 'interval': 'PT3H'},
                'identifier': (
                    'REPS.MEM.ETA_PN.01-20201122000000-20201122000000'),
                'layer_config': {'forecast_hours': '00/72/PT3H'},
                'layer_name': 'REPS.MEM.ETA_PN.01',
                'layer_name_unformatted': 'REPS.MEM.ETA_PN.{}',
                'member': '1',
                'model': 'reps',
                'reference_datetime': '2020-11-22T00:00:00Z',
                'refresh_config': True,
                'register_status': True,
            }
        ]
        self.assertListEqual(expected_items, self.layer_handler['reps'].items)

    def test_invalid_interval_identify(self):
        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['reps'].identify(self.filepath))

        # assert item returned is the same with register_status False
        self.expected_items[0]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['reps'].items
        )

    def test_unsuccessful_identify(self):
        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace(
            'TPRATE-Accum-3h_SFC_0', 'Not_wx_variable'
        )
        self.assertFalse(self.layer_handler['reps'].identify(self.filepath))


if __name__ == '__main__':
    unittest.main()
