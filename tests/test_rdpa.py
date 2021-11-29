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


class TestRdpaLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'rdpa', 'RdpaLayer')

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
            'name': 'rdpa',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        rdpa_layer_attr = self.layer_handler['rdpa'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, rdpa_layer_attr, msg=None)

    def test_super_init(self):

        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'rdpa'})


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'rdpa', 'RdpaLayer')
        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.rdpa.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'rdpa': {
                    'filename_pattern': {
                        '15km': 'CMC_RDPA_{wx_variable}_ps15km_{YYYYMMDD_model_run}_{forecast_hour}.grib2',  # noqa
                        '10km': 'CMC_RDPA_{wx_variable}_ps10km_{YYYYMMDD_model_run}_{forecast_hour}.grib2',  # noqa
                    },
                    'variable': {
                        'APCP-006-0700cutoff_SFC_0': {
                            'geomet_layers': {
                                'RDPA.6P_PR': {
                                    'forecast_hours': '-720/000/PT6H'
                                },
                                'RDPA.ARC_15km.6F_PR': {
                                    'begin': '2011-04-06T00:00:00Z',
                                    'end': '2012-10-03T00:00:00Z',
                                    'interval': 'PT6H',
                                },
                                'RDPA.6F_PR': {
                                    'begin': '2012-10-03T06:00:00Z',
                                    'interval': 'PT6H',
                                },
                            },
                            'model_run': {'00Z': {'files_expected': '1'}},
                            'elevation': 'surface',
                            'members': 'null',
                        }
                    },
                }
            }
        )

        self.filepath = './geomet_data_registry/tests/rdpa/grib2/forecast/raw/2020/11/CMC_RDPA_APCP-006-0700cutoff_SFC_0_ps10km_2021100100_-720.grib2'  # noqa
        self.layer_handler['rdpa'].filepath = self.filepath

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

        self.super_identify_patcher.stop()

    def test_successful_identify(self):

        # assert file was successfully identified
        self.assertTrue(self.layer_handler['rdpa'].identify(self.filepath))

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_ps15km2021_identify(self):

        expected_items = [
            {
                'elevation': 'surface',
                'expected_count': '1',
                'filepath': self.filepath,
                'forecast_hour_datetime': '2021-10-01T00:00:00Z',
                'forecast_hours': {
                    'begin': -720,
                    'end': 0,
                    'interval': 'PT6H',
                },
                'identifier': 'RDPA.6P_PR-20210901000000',
                'layer_config': {'forecast_hours': '-720/000/PT6H'},
                'layer_name': 'RDPA.6P_PR',
                'member': 'null',
                'model': 'rdpa',
                'reference_datetime': None,
                'refresh_config': True,
                'register_status': True,
            },
            {
                'elevation': 'surface',
                'expected_count': '1',
                'filepath': self.filepath,
                'forecast_hour_datetime': '2021-10-01T00:00:00Z',
                'forecast_hours': {
                    'begin': -78834.0,
                    'end': 0,
                    'interval': 'PT6H',
                },
                'identifier': 'RDPA.6F_PR-20210901000000',
                'layer_config': {
                    'begin': '2012-10-03T06:00:00Z',
                    'interval': 'PT6H',
                },
                'layer_name': 'RDPA.6F_PR',
                'member': 'null',
                'model': 'rdpa',
                'reference_datetime': None,
                'refresh_config': True,
                'register_status': True,
            },
        ]

        # assert you get the items above with the received JSON
        self.layer_handler['rdpa'].identify(self.filepath)
        self.assertListEqual(expected_items, self.layer_handler['rdpa'].items)

    def test_items_ps15km2011_identify(self):

        self.filepath = self.filepath.replace('ps10km_2021', 'ps15km_2011')
        self.layer_handler['rdpa'].filepath = self.filepath

        expected_items = [
            {
                'elevation': 'surface',
                'expected_count': '1',
                'filepath': self.filepath,
                'forecast_hour_datetime': '2011-10-01T00:00:00Z',
                'forecast_hours': {
                    'begin': -4272.0,
                    'end': 0,
                    'interval': 'PT6H',
                },
                'identifier': 'RDPA.ARC_15km.6F_PR-20110901000000',
                'layer_config': {
                    'begin': '2011-04-06T00:00:00Z',
                    'end': '2012-10-03T00:00:00Z',
                    'interval': 'PT6H',
                },
                'layer_name': 'RDPA.ARC_15km.6F_PR',
                'member': 'null',
                'model': 'rdpa',
                'reference_datetime': None,
                'refresh_config': True,
                'register_status': True,
            }
        ]

        # assert you get the item above with the received JSON
        self.layer_handler['rdpa'].identify(self.filepath)
        self.assertListEqual(expected_items, self.layer_handler['rdpa'].items)

    def test_unsuccessful_identify(self):

        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace(
            'APCP-006-0700cutoff_SFC_0', 'Not_wx_variable'
        )
        self.assertFalse(self.layer_handler['rdpa'].identify(self.filepath))


class TestAddTimeKey(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'rdpa', 'RdpaLayer')

        self.layer_handler['rdpa'].date_ = datetime(2021, 9, 27)

        self.items = [
            {
                'elevation': 'surface',
                'expected_count': '1',
                'filepath': './geomet_data_registry/tests/rdpa/grib2/forecast/raw/2021/09/CMC_RDPA_APCP-006-0700cutoff_SFC_0_ps15km_2021092700_-720.grib2',  # noqa: E501
                'forecast_hour_datetime': '2021-09-27T00:00:00Z',
                'forecast_hours': {
                    'begin': -91944.0,
                    'end': 0,
                    'interval': 'PT6H',
                },
                'identifier': 'RDPA.ARC_15km.6F_PR-20210927000000',
                'layer_config': {
                    'begin': '2011-04-06T00:00:00Z',
                    'end': '2012-10-03T00:00:00Z',
                    'interval': 'PT6H',
                },
                'layer_name': 'RDPA.ARC_15km.6F_PR',
                'member': 'null',
                'model': 'rdpa',
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

    def test_unsuccessful_add_time_key(self):
        self.layer_handler['rdpa'].add_time_key()

        # assert store.set_key isn't called if there are no items
        self.mocked_load_plugin.assert_not_called()

    def test_successful_add_time_key(self):
        self.layer_handler['rdpa'].items = self.items

        # arguments used with store.set_key
        start_time = datetime(2021, 9, 27) + timedelta(hours=-91944.0)
        start_time = start_time.strftime(DATE_FORMAT)
        end_time = datetime(2021, 9, 27).strftime(DATE_FORMAT)

        # make last_default_time_key < layer_handler['rdpa'].date_
        self.mocked_load_plugin.return_value.get_key.return_value = (
            '2021-9-26T00:00:00Z'
        )

        self.layer_handler['rdpa'].add_time_key()

        # assert these 2 calls were made with store.set_key
        calls = [
            call('RDPA.ARC_15km.6F_PR_default_time', end_time),
            call(
                'RDPA.ARC_15km.6F_PR_time_extent',
                '{}/{}/PT6H'.format(start_time, end_time),
            ),
        ]
        self.mocked_load_plugin.return_value.set_key.assert_has_calls(
            calls, any_order=True
        )

    def test_not_updating_add_time_key(self):
        self.layer_handler['rdpa'].items = self.items

        # make last_default_time_key > layer_handler['rdpa'].date_
        self.mocked_load_plugin.return_value.get_key.return_value = (
            '2021-9-28T00:00:00Z'
        )
        self.layer_handler['rdpa'].add_time_key()

        # assert store.set_key isn't called if
        # last_default_time_key > layer_handler['rdpa'].date_
        self.mocked_load_plugin.return_value.get_key.assert_called_with(
            '{}_default_time'.format(self.items[0]['layer_name'])
        )
        self.mocked_load_plugin.return_value.set_key.assert_not_called()


if __name__ == '__main__':
    unittest.main()
