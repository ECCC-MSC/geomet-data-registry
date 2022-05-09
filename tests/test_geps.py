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


class TestGepsLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'geps', 'GepsLayer')

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
            'name': 'geps',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
            'type': None,
            'bands': None,
        }

        geps_layer_attr = self.layer_handler['geps'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, geps_layer_attr, msg=None)

    def test_super_init(self):
        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'geps'})

    def test_repr(self):
        self.assertEqual(
            repr(self.layer_handler['geps']),
            '<ModelGEPSLayer> geps'
        )


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'geps', 'GepsLayer')

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.geps.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        self.is_valid_patcher = patch(
            'geomet_data_registry.layer.geps.BaseLayer.is_valid_interval'
        )
        self.mocked_valid_interval = self.is_valid_patcher.start()

        self.filepath = './geomet_data_registry/tests/data/geps/grib2/forecast/raw/2020/11/CMC_geps-prob_HEATX_TGL_2m_latlon0p5x0p5_202011220_P001_all-products.grib2'  # noqa
        self.layer_handler['geps'].filepath = self.filepath

        # make store.get_key return this JSON string (product)
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'geps': {
                    'product': {
                        'filename_pattern': 'CMC_geps-prob_{wx_variable}_latlon0p5x0p5_{YYYYMMDD_model_run}_P{forecast_hour}_all-products.grib2',  # noqa
                        'variable': {
                            'HEATX_TGL_2m': {
                                'geomet_layers': {
                                    'GEPS.DIAG.3_HMX.{}': {
                                        'forecast_hours': '003/384/PT3H'
                                    }
                                },
                                'bands': {'1': {'product': 'ERC10'}},
                                'elevation': '2m',
                                'model_run': {
                                    '00Z': {'files_expected': '128'}
                                },
                                'members': 'null',
                            }
                        },
                    },
                    'model_run_retention_hours': '72',
                    'model_run_interval_hours': '12',
                }
            }
        )

        self.expected_items = [
            {
                'elevation': '2m',
                'expected_count': '128',
                'filepath': 'vrt://{}?bands=1'.format(self.filepath),
                'forecast_hour_datetime': '2020-11-22T01:00:00Z',
                'forecast_hours': {'begin': 3, 'end': 384, 'interval': 'PT3H'},
                'identifier': (
                    'GEPS.DIAG.3_HMX.ERC10-20201122000000-20201122010000'
                ),
                'layer_config': {'forecast_hours': '003/384/PT3H'},
                'layer_name': 'GEPS.DIAG.3_HMX.ERC10',
                'layer_name_unformatted': 'GEPS.DIAG.3_HMX.{}',
                'member': None,
                'model': 'geps',
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
        self.assertTrue(self.layer_handler['geps'].identify(self.filepath))

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_product_identify(self):
        # assert you get expected items with the received JSON
        self.layer_handler['geps'].identify(self.filepath)
        self.assertListEqual(
            self.expected_items, self.layer_handler['geps'].items
        )

    def test_member_identify(self):
        # make store.get_key return this JSON string (member)
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'geps': {
                    'member': {
                        'filename_pattern': 'CMC_geps-prob_{wx_variable}_latlon0p5x0p5_{YYYYMMDD_model_run}_P{forecast_hour}_allmbrs.grib2',  # noqa
                        'variable': {
                            'HEATX_TGL_2m': {
                                'geomet_layers': {
                                    'GEPS.DIAG.3_HMX.{}': {
                                        'forecast_hours': '003/384/PT3H'
                                    }
                                },
                                'elevation': '2m',
                                'model_run': {
                                    '00Z': {'files_expected': '128'}
                                },
                            }
                        },
                        'bands': {'1': {'member': '1'}},
                    },
                    'model_run_retention_hours': '72',
                    'model_run_interval_hours': '12',
                    'members': '20',
                }
            }
        )

        filepath = self.filepath.replace('all-products', 'allmbrs')
        self.layer_handler['geps'].filepath = filepath

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['geps'].identify(filepath))

        # assert these are the only params that changed from expected items
        self.expected_items[0]['filepath'] = 'vrt://{}?bands=1'.format(
            filepath
        )
        member = '1'
        self.expected_items[0]['member'] = member
        self.expected_items[0]['identifier'] = (
            f'GEPS.DIAG.3_HMX.{member}-20201122000000-20201122010000')
        self.expected_items[0]['layer_name'] = f'GEPS.DIAG.3_HMX.{member}'
        self.assertListEqual(
            self.expected_items, self.layer_handler['geps'].items
        )

    def test_invalid_interval_identify(self):
        # make self.is_valid_interval return False
        self.mocked_valid_interval.return_value = False

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['geps'].identify(self.filepath))

        # assert item returned is the same with register_status False
        self.expected_items[0]['register_status'] = False
        self.assertListEqual(
            self.expected_items, self.layer_handler['geps'].items
        )

    def test_unsuccessful_identify(self):
        # assert identify returns False when the wx_variable
        # isn't correct and a warning is logged.
        self.filepath = self.filepath.replace(
            'HEATX_TGL_2m', 'Not_wx_variable'
        )
        with self.assertLogs(
            'geomet_data_registry.layer.geps', level='WARNING'
        ) as warn:
            self.assertFalse(
                self.layer_handler['geps'].identify(self.filepath)
            )
            # assert a single LOGGER.warning was called
            self.assertEqual(len(warn.records), 1)


if __name__ == '__main__':
    unittest.main()
