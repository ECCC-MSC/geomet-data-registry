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

from datetime import datetime
import json
import unittest
from unittest.mock import patch, call

from dateutil.relativedelta import relativedelta

from geomet_data_registry.util import DATE_FORMAT
from .setup_test_class import Setup


class TestCansips(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'cansips', 'CansipsLayer')

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
            'name': 'cansips',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        cansips_layer_attr = self.layer_handler['cansips'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, cansips_layer_attr, msg=None)

    def test_super_init(self):
        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'cansips'})


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'cansips', 'CansipsLayer')
        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.cansips.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'cansips': {
                    'filename_pattern': 'cansips_forecast_raw_latlon{resolution}_{wx_variable}_{pressure}_{pres_value}_{YYYY}-{MM}_allmembers.grib2',  # noqa
                    'variable': {
                        'PRATE_SFC_0': {
                            'geomet_layers': {
                                'CANSIPS.MEM.ETA_RT.{}': {
                                    'forecast_hours': '00/12/P1M',
                                    'begin': '2013-05-01T00:00:00Z',
                                }
                            },
                            'elevation': 'surface',
                        }
                    },
                    'bands': {
                        '1': {'member': '1', 'forecast_interval': 'P0M'}
                    },
                }
            }
        )

        self.filepath = './geomet_data_registry/tests/data/cansips/grib2/forecast/raw/2020/11/cansips_forecast_raw_latlon.5x2.5_PRATE_SFC_0_2020-11_allmembers.grib2'  # noqa
        self.layer_handler['cansips'].filepath = self.filepath

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

        self.super_identify_patcher.stop()

    def test_successful_identify(self):
        # assert file was successfully identified
        self.assertTrue(self.layer_handler['cansips'].identify(self.filepath))

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify(self):
        expected_items = [
            {
                'elevation': 'surface',
                'expected_count': None,
                'filepath': 'vrt://{}?bands=1'.format(self.filepath),
                'forecast_hour_datetime': '2020-11-01T00:00:00Z',
                'forecast_hours': {
                    'begin': '00',
                    'end': '12',
                    'interval': 'P1M',
                },
                'identifier': (
                    'CANSIPS.MEM.ETA_RT.01-20201101000000-20201101000000'
                ),
                'layer_config': {
                    'begin': '2013-05-01T00:00:00Z',
                    'forecast_hours': '00/12/P1M',
                },
                'layer_name': 'CANSIPS.MEM.ETA_RT.01',
                'member': '1',
                'model': 'cansips',
                'reference_datetime': '2020-11-01T00:00:00Z',
                'register_status': True,
                'static_model_run': {'begin': '2013-05-01T00:00:00Z'},
            }
        ]

        # assert you get the item above with the received JSON
        self.layer_handler['cansips'].identify(self.filepath)
        self.assertListEqual(
            expected_items, self.layer_handler['cansips'].items
        )

    def test_unsuccessful_identify(self):
        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace('PRATE_SFC_0', 'Not_wx_variable')
        self.assertFalse(self.layer_handler['cansips'].identify(self.filepath))


class TestAddTimeKey(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'cansips', 'CansipsLayer')

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

    def test_unsuccessful_add_time_key(self):
        self.layer_handler['cansips'].add_time_key()

        # assert store.set_key isn't called if there are no items
        self.mocked_load_plugin.assert_not_called()

    def test_successful_add_time_key(self):
        self.layer_handler['cansips'].date_ = datetime(2021, 9, 27)
        self.layer_handler['cansips'].items = [
            {
                'elevation': 'surface',
                'expected_count': None,
                'filepath': './geomet_data_registry/tests/data/cansips/grib2/forecast/raw/2020/11/cansips_forecast_raw_latlon.5x2.5_PRATE_SFC_0_2020-11_allmembers.grib2',  # noqa
                'forecast_hour_datetime': '2020-11-01T00:00:00Z',
                'forecast_hours': {
                    'begin': '00',
                    'end': '12',
                    'interval': 'P1M',
                },
                'identifier': (
                    'CANSIPS.MEM.ETA_RT.01-20201101000000-20201101000000'
                ),
                'layer_config': {
                    'begin': '2013-05-01T00:00:00Z',
                    'forecast_hours': '00/12/P1M',
                },
                'layer_name': 'CANSIPS.MEM.ETA_RT.01',
                'member': '1',
                'model': 'cansips',
                'reference_datetime': '2020-11-01T00:00:00Z',
                'register_status': True,
                'static_model_run': {'begin': '2013-05-01T00:00:00Z'},
            }
        ]

        self.layer_handler['cansips'].add_time_key()

        # arguments used with store.set_key
        start_time = datetime(2021, 9, 27) + relativedelta(months=int('00'))
        start_time = start_time.strftime(DATE_FORMAT)
        end_time = datetime(2021, 9, 27) + relativedelta(months=int('12'))
        end_time = end_time.strftime(DATE_FORMAT)
        date_formatted = datetime(2021, 9, 27).strftime(DATE_FORMAT)

        # assert these 3 calls were made with store.set_key
        calls = [
            call(
                'CANSIPS.MEM.ETA_RT.01_time_extent',
                '{}/{}/P1M'.format(start_time, end_time),
            ),
            call('CANSIPS.MEM.ETA_RT.01_default_model_run', date_formatted),
            call(
                'CANSIPS.MEM.ETA_RT.01_model_run_extent',
                '2013-05-01T00:00:00Z/{}/P1M'.format(date_formatted),
            ),
        ]
        self.mocked_load_plugin.return_value.set_key.assert_has_calls(
            calls, any_order=True
        )


if __name__ == '__main__':
    unittest.main()
