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

from geomet_data_registry.util import DATE_FORMAT
from .setup_test_class import Setup


class TestModelRdaqaCeLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(
            self, 'model_rdaqa_ce', 'ModelRdaqaCeLayer', 'model_rdaqa-ce'
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
            'name': 'model_rdaqa-ce',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        model_rdaqa_ce_layer_attr = (
            self.layer_handler['model_rdaqa_ce'].__dict__
        )

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(
            expected_values, model_rdaqa_ce_layer_attr, msg=None
        )

    def test_super_init(self):

        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'model_rdaqa-ce'})


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(
            self, 'model_rdaqa_ce', 'ModelRdaqaCeLayer', 'model_rdaqa-ce'
        )

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.model_rdaqa_ce.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'model_rdaqa-ce': {
                    'filename_pattern': '{YYYYMMDD_model_run}_MSC_RDAQA_{wx_variable}_RLatLon0.09x0.09_{interval}.nc',  # noqa
                    'variable': {
                        'O3-MAvg_SFC': {
                            'geomet_layers': {
                                'RDAQA.CE_O3-MAvg': {'interval': 'P1M'}
                            },
                            'elevation': 'surface',
                            'members': 'null',
                            'model_run': {'00Z': {'files_expected': '1'}},
                        }
                    },
                }
            }
        )

        self.filepath = './geomet_data_registry/tests/data/model_rdaqa_ce/grib2/forecast/raw/2020/11/20201122T0Z_MSC_RDAQA_O3-MAvg_SFC_RLatLon0.09x0.09_P1M.nc'  # noqa
        self.layer_handler['model_rdaqa_ce'].filepath = self.filepath

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

        self.super_identify_patcher.stop()

    def test_successful_identify(self):

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['model_rdaqa_ce'].identify(self.filepath)
        )

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify(self):

        expected_items = [
            {
                'elevation': 'surface',
                'expected_count': None,
                'filepath': self.filepath,
                'forecast_hour_datetime': '2020-11-22T00:00:00Z',
                'identifier': 'RDAQA.CE_O3-MAvg-20201122000000',
                'layer_config': {'interval': 'P1M'},
                'layer_name': 'RDAQA.CE_O3-MAvg',
                'member': 'null',
                'model': 'model_rdaqa-ce',
                'reference_datetime': None,
                'refresh_config': True,
                'register_status': True,
            }
        ]

        # assert you get the item above with the received JSON
        self.layer_handler['model_rdaqa_ce'].identify(self.filepath)
        self.assertListEqual(
            expected_items, self.layer_handler['model_rdaqa_ce'].items
        )

    def test_unsuccessful_identify(self):

        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace('O3-MAvg_SFC', 'Not_wx_variable')
        self.assertFalse(
            self.layer_handler['model_rdaqa_ce'].identify(self.filepath)
        )


class TestAddTimeKey(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(
            self, 'model_rdaqa_ce', 'ModelRdaqaCeLayer', 'model_rdaqa-ce'
        )

        self.date_formatted = datetime(2021, 9, 27).strftime(DATE_FORMAT)

        self.layer_handler['model_rdaqa_ce'].interval = 'P1M'
        self.layer_handler['model_rdaqa_ce'].date_ = datetime(2021, 9, 27)

        self.items = [
            {
                'elevation': 'surface',
                'expected_count': None,
                'filepath': './geomet_data_registry/tests/data/model_rdaqa_ce/grib2/forecast/raw/2020/11/20201122T0Z_MSC_RDAQA_O3-MAvg_SFC_RLatLon0.09x0.09_P1M.nc',  # noqa
                'forecast_hour_datetime': '2020-11-22T00:00:00Z',
                'identifier': 'RDAQA.CE_O3-MAvg-20201122000000',
                'layer_config': {'interval': 'P1M'},
                'layer_name': 'RDAQA.CE_O3-MAvg',
                'member': 'null',
                'model': 'model_rdaqa-ce',
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

        self.layer_handler['model_rdaqa_ce'].add_time_key()

        # assert store.set_key isn't called if there are no items
        self.mocked_load_plugin.assert_not_called()

    def test_add_time_key_none(self):

        self.layer_handler['model_rdaqa_ce'].items = self.items

        # make last_default_time_key equal to None
        self.mocked_load_plugin.return_value.get_key.return_value = None

        # assert these 2 calls were made with store.set_key
        calls = [
            call('RDAQA.CE_O3-MAvg_default_time', self.date_formatted),
            call(
                'RDAQA.CE_O3-MAvg_time_extent',
                '{}/{}/P1M'.format(self.date_formatted, self.date_formatted),
            ),
        ]
        self.assertTrue(self.layer_handler['model_rdaqa_ce'].add_time_key())
        self.mocked_load_plugin.return_value.set_key.assert_has_calls(
            calls, any_order=True
        )

    def test_add_time_key_prev_begin(self):

        self.layer_handler['model_rdaqa_ce'].items = self.items

        # store.get_key() will return these values in sequence like a generator
        # (last_default_time_key, last_default_extent_key)
        self.mocked_load_plugin.return_value.get_key.side_effect = [
            '2021-9-27T00:00:00Z',
            '{}/{}'.format('2021-9-28T00:00:00Z', '2021-10-30T00:00:00Z'),
        ]

        prev_int_end_formatted = datetime(2021, 10, 30).strftime(DATE_FORMAT)
        # expected arguments used with store.set_key
        call_args = (
            'RDAQA.CE_O3-MAvg_time_extent',
            '{}/{}/P1M'.format(self.date_formatted, prev_int_end_formatted),
        )

        # assert store.set_key called only once with the args above
        self.assertTrue(self.layer_handler['model_rdaqa_ce'].add_time_key())
        self.mocked_load_plugin.return_value.set_key.assert_called_once_with(
            *call_args
        )

    def test_add_time_key_prev_default_prev_end(self):

        self.layer_handler['model_rdaqa_ce'].items = self.items

        # argument used with store.set_key
        prev_int_begin_formatted = datetime(2021, 9, 24).strftime(DATE_FORMAT)

        # store.get_key() will return these values in sequence like a generator
        # (last_default_time_key, last_default_extent_key)
        self.mocked_load_plugin.return_value.get_key.side_effect = [
            '2021-9-26T00:00:00Z',
            '{}/{}'.format('2021-9-24T00:00:00Z', '2021-9-25T00:00:00Z'),
        ]

        # assert these 2 calls were made with store.set_key
        calls = [
            call(
                'RDAQA.CE_O3-MAvg_time_extent',
                '{}/{}/P1M'.format(
                    prev_int_begin_formatted, self.date_formatted
                ),
            ),
            call('RDAQA.CE_O3-MAvg_default_time', self.date_formatted),
        ]

        self.assertTrue(self.layer_handler['model_rdaqa_ce'].add_time_key())
        self.mocked_load_plugin.return_value.set_key.assert_has_calls(
            calls, any_order=True  # noqa
        )


if __name__ == '__main__':
    unittest.main()
