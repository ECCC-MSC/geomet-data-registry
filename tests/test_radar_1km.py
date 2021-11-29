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


class TestRadar1kmLayer(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'radar_1km', 'Radar1kmLayer', 'Radar_1km')

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
            'name': 'Radar_1km',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        radar_1km_layer_attr = self.layer_handler['radar_1km'].__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, radar_1km_layer_attr, msg=None)

    def test_super_init(self):

        # assert super().__init__() was called with the correct provider def
        self.mocked_base_init.assert_called_with({'name': 'Radar_1km'})


class TestIdentify(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'radar_1km', 'Radar1kmLayer', 'Radar_1km')

        self.super_identify_patcher = patch(
            'geomet_data_registry.layer.radar_1km.BaseLayer.identify'
        )
        self.mocked_base_identify = self.super_identify_patcher.start()

        # make store.get_key return this JSON string
        self.mocked_load_plugin.return_value.get_key.return_value = json.dumps(
            {
                'radar': {
                    'filename_pattern': '{YYYYMMDDThhmm}Z_MSC_Radar-Composite_{precipitation_type}_1km.tif',  # noqa
                    'variable': {
                        'MMHR': {
                            'geomet_layers': 'RADAR_1KM_RRAI',
                            'forecast_hours': '-180/000/PT10M',
                            'elevation': 'null',
                            'members': 'null',
                        }
                    },
                }
            }
        )

        self.filepath = './geomet_data_registry/tests/data/RADAR/1KM/MMHR/20211130T1400Z_MSC_Radar-Composite_MMHR_1km.tif'  # noqa
        self.layer_handler['radar_1km'].filepath = self.filepath

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

        self.super_identify_patcher.stop()

    def test_successful_identify(self):

        # assert file was successfully identified
        self.assertTrue(
            self.layer_handler['radar_1km'].identify(self.filepath)
        )

        # assert super().identify() was called with these args
        self.mocked_base_identify.assert_called_with(self.filepath, None)

    def test_items_identify(self):

        expected_items = [
            {
                'elevation': 'null',
                'expected_count': None,
                'filepath': self.filepath,
                'forecast_hour_datetime': '2021-11-30T14:00:00Z',
                'identifier': 'RADAR_1KM_RRAI-20211130140000',
                'layer_config': {
                    'elevation': 'null',
                    'forecast_hours': '-180/000/PT10M',
                    'geomet_layers': 'RADAR_1KM_RRAI',
                    'members': 'null',
                },
                'layer_name': 'RADAR_1KM_RRAI',
                'member': 'null',
                'model': 'radar',
                'reference_datetime': None,
                'refresh_config': True,
                'register_status': True,
            }
        ]

        # assert you get the item above with the received JSON
        self.layer_handler['radar_1km'].identify(self.filepath)
        self.assertListEqual(
            expected_items, self.layer_handler['radar_1km'].items
        )

    def test_unsuccessful_identify(self):

        # assert identify returns False when the wx_variable isn't correct
        self.filepath = self.filepath.replace('MMHR', 'Not_wx_variable')
        self.assertFalse(
            self.layer_handler['radar_1km'].identify(self.filepath)
        )


class TestAddTimeKey(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'radar_1km', 'Radar1kmLayer', 'Radar_1km')

        self.layer_handler['radar_1km'].date_ = (
            datetime(2021, 11, 30, 14, 00, 00)
        )
        self.layer_handler['radar_1km'].model = 'radar'
        self.layer_handler['radar_1km'].wx_variable = 'MMHR'
        self.layer_handler['radar_1km'].file_dict = {
            'radar': {
                'filename_pattern': '{YYYYMMDDhhmm}_RADAR_COMPOSITE_1KM_{precipitation_type}.tif',  # noqa
                'variable': {
                    'MMHR': {
                        'geomet_layers': 'RADAR_1KM_RRAI',
                        'forecast_hours': '-180/000/PT10M',
                        'elevation': 'null',
                        'members': 'null',
                    }
                },
            }
        }

        self.layer_handler['radar_1km'].items = [
            {
                'layer_name': 'RADAR_1KM_RRAI',
                'layer_config': {
                    'geomet_layers': 'RADAR_1KM_RRAI',
                    'forecast_hours': '-180/000/PT10M',
                    'elevation': None,
                    'members': None,
                },
                'filepath': './geomet_data_registry/tests/data/RADAR/1KM/MMHR/20211130T1400Z_MSC_Radar-Composite_MMHR_1km.tif',  # noqa
                'identifier': 'RADAR_1KM_RRAI-20211130140000',
                'reference_datetime': None,
                'forecast_hour_datetime': '2021-11-30T14:00:00Z',
                'member': None,
                'model': 'radar',
                'elevation': None,
                'expected_count': None,
                'register_status': True,
                'refresh_config': True,
            }
        ]

        self.date_formatted = datetime(2021, 11, 30, 14, 00, 00).strftime(
            DATE_FORMAT
        )
        self.start_time = datetime(2021, 11, 30, 14, 00, 00) + timedelta(
            minutes=int('-180')
        )
        self.start_time = self.start_time.strftime(DATE_FORMAT)

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.init_patcher.stop()

    def test_successful_add_time_key_none(self):

        # make last_key equal to None
        self.mocked_load_plugin.return_value.get_key.return_value = None

        # assert time key was successfully added
        self.assertTrue(self.layer_handler['radar_1km'].add_time_key())

        # assert these 2 calls were made with store.set_key
        calls = [
            call('RADAR_1KM_RRAI_default_time', self.date_formatted),
            call(
                'RADAR_1KM_RRAI_time_extent',
                '{}/{}/PT10M'.format(self.start_time, self.date_formatted),
            ),
        ]
        self.mocked_load_plugin.return_value.set_key.assert_has_calls(
            calls, any_order=True
        )

    def test_successful_add_time_key_missed_timestep(self):
        # make last_key equal to layer_handler['radar_1km'].date_ minus 20min
        self.mocked_load_plugin.return_value.get_key.return_value = (
            '2021-11-30T13:40:00Z'
        )

        # assert time key was successfully added
        self.assertTrue(self.layer_handler['radar_1km'].add_time_key())

        # assert these 2 calls were made with store.set_key
        calls = [
            call('RADAR_1KM_RRAI_default_time', self.date_formatted),
            call(
                'RADAR_1KM_RRAI_time_extent',
                '{}/{}/PT10M'.format(self.start_time, self.date_formatted),
            ),
        ]
        self.mocked_load_plugin.return_value.set_key.assert_has_calls(
            calls, any_order=True
        )


if __name__ == '__main__':
    unittest.main()
