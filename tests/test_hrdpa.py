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

from datetime import datetime, timedelta
import json
import unittest
from unittest.mock import patch, call

from geomet_data_registry.util import DATE_FORMAT
from .setup_test_class import Setup


class TestHrdpaLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'hrdpa', 'HrdpaLayer')

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
            'name': 'hrdpa',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        hrdpa_layer_attr = self.layer_handler['hrdpa'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, hrdpa_layer_attr, msg=None)

    def test_super_init(self):
        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'hrdpa'})

    def test_repr(self):
        self.assertEqual(
            repr(self.layer_handler['hrdpa']),
            '<HrdpaLayer> hrdpa'
        )


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'hrdpa', 'HrdpaLayer')

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.hrdpa.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'hrdpa': {
                    'filename_pattern': 'CMC_HRDPA_{wx_variable}_ps2.5km_{YYYYMMDD_model_run}_{forecast_hour}.grib2',  # noqa
                    'variable': {
                        'APCP-006-0100cutoff_SFC_0': {
                            'geomet_layers': {
                                'HRDPA.6P_PR': {
                                    'forecast_hours': '-720/000/PT6H'
                                }
                            },
                            'bands': {'1': {'product': 'ERC10'}},
                            'elevation': 'surface',
                            'model_run': {'00Z': {'files_expected': '1'}},
                            'members': 'null',
                        }
                    },
                }
            }
        )

        self.filepath = './geomet_data_registry/tests/data/hrdpa/grib2/forecast/raw/2020/11/CMC_HRDPA_APCP-006-0100cutoff_SFC_0_ps2.5km_202011220_001.grib2'  # noqa
        self.layer_handler['hrdpa'].filepath = self.filepath

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

        self.super_identify_patcher.stop()

    def test_successful_identify(self):

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['hrdpa'].identify(self.filepath))

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify(self):

        expected_items = [
            {
                'elevation': 'surface',
                'expected_count': '1',
                'filepath': self.filepath,
                'forecast_hour_datetime': '2020-11-22T00:00:00Z',
                'forecast_hours': {
                    'begin': -720,
                    'end': 0,
                    'interval': 'PT6H',
                },
                'identifier': 'HRDPA.6P_PR-20201122010000',
                'layer_config': {'forecast_hours': '-720/000/PT6H'},
                'layer_name': 'HRDPA.6P_PR',
                'member': 'null',
                'model': 'hrdpa',
                'reference_datetime': None,
                'refresh_config': True,
                'register_status': True,
            }
        ]

        # assert you get the item above with the received JSON
        self.layer_handler['hrdpa'].identify(self.filepath)
        self.assertListEqual(expected_items, self.layer_handler['hrdpa'].items)

    def test_unsuccessful_identify(self):
        # assert identify returns False when the wx_variable
        # isn't correct and a warning is logged.
        self.filepath = self.filepath.replace(
            'APCP-006-0100cutoff_SFC_0', 'Not_wx_variable'
        )
        with self.assertLogs(
            'geomet_data_registry.layer.hrdpa', level='WARNING'
        ) as warn:
            self.assertFalse(
                self.layer_handler['hrdpa'].identify(self.filepath)
            )
            # assert a single LOGGER.warning was called
            self.assertEqual(len(warn.records), 1)


class TestAddTimeKey(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'hrdpa', 'HrdpaLayer')

        self.layer_handler['hrdpa'].date_ = datetime(2021, 9, 27)
        self.items = [
            {
                'elevation': 'surface',
                'expected_count': '1',
                'filepath': './geomet_data_registry/tests/data/hrdpa/grib2/forecast/raw/2020/11/CMC_HRDPA_APCP-006-0100cutoff_SFC_0_ps2.5km_202011220_001.grib2',  # noqa
                'forecast_hour_datetime': '2020-11-22T00:00:00Z',
                'forecast_hours': {
                    'begin': -720,
                    'end': 0,
                    'interval': 'PT6H',
                },
                'identifier': 'HRDPA.6P_PR-20201122010000',
                'layer_config': {'forecast_hours': '-720/000/PT6H'},
                'layer_name': 'HRDPA.6P_PR',
                'member': 'null',
                'model': 'hrdpa',
                'reference_datetime': None,
                'refresh_config': True,
                'register_status': True,
            }
        ]

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

    def test_empty_items_add_time_key(self):

        self.layer_handler['hrdpa'].add_time_key()

        # assert store.get_key and store.set_key not called if items are empty
        self.mocked_load_plugin.assert_not_called()

    def test_wrong_date_add_time_key(self):

        self.layer_handler['hrdpa'].items = self.items
        # make store.get_key return date > layer_handler['hrdpa'].date_
        self.mocked_load_plugin.return_value.get_key.return_value = (
            '2021-9-28T00:00:00Z'
        )
        self.layer_handler['hrdpa'].add_time_key()

        # assert store.set_key was not called
        self.mocked_load_plugin.return_value.set_key.assert_not_called()

    def test_successful_add_time_key(self):

        self.layer_handler['hrdpa'].items = self.items
        # make store.get_key return date = layer_handler['hrdpa'].date_
        self.mocked_load_plugin.return_value.get_key.return_value = (
            '2021-9-27T00:00:00Z'
        )

        # assert time key was successfully added
        self.assertTrue(self.layer_handler['hrdpa'].add_time_key())

        # arguments used with store.set_key
        end_time = self.layer_handler['hrdpa'].date_.strftime(DATE_FORMAT)
        start_time = (
            self.layer_handler['hrdpa'].date_ + timedelta(hours=-720)
        ).strftime(DATE_FORMAT)

        # assert these 2 calls were made with store.set_key
        calls = [
            call('HRDPA.6P_PR_default_time', end_time),
            call(
                'HRDPA.6P_PR_time_extent',
                '{}/{}/PT6H'.format(start_time, end_time),
            ),
        ]
        self.mocked_load_plugin.return_value.set_key.assert_has_calls(
            calls, any_order=True
        )


if __name__ == '__main__':
    unittest.main()
