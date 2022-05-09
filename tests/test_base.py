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
import unittest
from unittest.mock import patch, call

from geomet_data_registry.tileindex.base import TileNotFoundError
from geomet_data_registry.util import DATE_FORMAT
from .setup_test_class import Setup


class TestSingleAssert(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_gem_global', 'BaseLayer')

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()

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
            'name': 'model_gem_global',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        base_layer_attr = self.base_layer.__dict__

        # assert that these are the values for the attributes
        # and that there are no attributes missing or extra
        self.assertDictEqual(expected_values, base_layer_attr, msg=None)

    def test_identify(self):

        filepath = './geomet_data_registry/tests/data/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_UGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2'  # noqa

        expected_values = {
            'items': [],
            'model_run_list': [],
            'receive_datetime': self.today_date,
            'identify_datetime': None,
            'register_datetime': None,
            'filepath': filepath,
            'url': 'https://dd4.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_VGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2',  # noqa
            'dimensions': None,
            'model': None,
            'model_run': None,
            'geomet_layers': None,
            'wx_variable': None,
            'date_': None,
            'file_dict': None,
            'new_key_store': False,
            'name': 'model_gem_global',
            'store': self.mocked_load_plugin.return_value,
            'tileindex': self.mocked_load_plugin.return_value,
        }

        base_layer_attr = self.base_layer.__dict__

        self.base_layer.identify(
            filepath,
            'https://dd4.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_VGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2',  # noqa
        )

        # assert that all identify() does is change filepath and url
        self.assertDictEqual(expected_values, base_layer_attr, msg=None)

    @patch('geomet_data_registry.layer.base.VRTDataset')
    def test_configure_layer_with_dependencies(self, mocked_vrtdataset):
        """
        Test that
        geomet_data_registry.layer.base.configure_layer_with_dependencies()
        returns a tuple containing a VRT (mocked), list of URLS, and
        a list of the weather variables.
        """

        # Simulate GDPS UGRD_TGL_10 layer
        self.base_layer.url = 'https://dd4.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_UGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2'  # noqa
        self.base_layer.wx_variable = 'UGRD_TGL_10'

        # Extract VGRD_TGL_10 dependency only from mocked dependencies list
        dependencies = [self.create_dependencies()[1]]

        # set remaining params need for configuring VRT
        image_dimension = {'x': 2401, 'y': 1201}
        bands_order = ['UGRD_TGL_10', 'VGRD_TGL_10']

        formatted_vrt_expected = '<VRTDataset>...</VRTDataset>'

        urls_expected = [
            'https://dd4.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_UGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2',  # noqa
            'https://dd4.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_VGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2',  # noqa
        ]
        weather_variables_expected = ['UGRD_TGL_10', 'VGRD_TGL_10']

        # make VRTDataset return '<VRTDataset>...</VRTDataset>'
        mocked_vrtdataset.return_value.build.return_value = (
            formatted_vrt_expected
        )

        [
            vrt,
            urls,
            weather_variables,
        ] = self.base_layer.configure_layer_with_dependencies(
            dependencies, image_dimension, bands_order
        )

        # assert weather_variables, urls and vrt are expected values
        self.assertListEqual(
            [
                formatted_vrt_expected,
                urls_expected,
                weather_variables_expected,
            ],
            [vrt, urls, weather_variables],
        )

    def test_is_valid_interval(self):
        """
        Test that the the geomet_data_registry.layer.base.is_valid_interval()
        method returns the appropriate value given the input arguments.
        """

        return_list = []

        # assert returns True if forecast hour and interval are 0
        # (when data is only avaiable at 000 forecast hour)
        return_list.append(self.base_layer.is_valid_interval(0, 0, 0, 0))

        # assert returns True if forecast hour (12) is an acceptable
        # interval value for a given time range (0-240) and interval (3 hours)
        return_list.append(self.base_layer.is_valid_interval(12, 0, 240, 3))

        # assert returns False when forecast hour  is not an acceptable
        # interval for given time range and interval.
        return_list.append(self.base_layer.is_valid_interval(7, 0, 240, 3))

        self.assertListEqual(return_list, [True, True, False])

    def test_repr(self):
        self.assertEqual(
            repr(self.base_layer),
            '<BaseLayer> model_gem_global'
        )


class TestRegister(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_gem_global', 'BaseLayer')

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()

    def test_register_no_items(self):
        """
        Test that when no items are identified
        geomet_data_registry.layer.base.register()
        returns False and an error is logged.
        """
        with self.assertLogs(
            'geomet_data_registry.layer.base', level='ERROR'
        ) as err:
            self.assertFalse(self.base_layer.register())
            # assert a single LOGGER.error was called
            self.assertEqual(len(err.records), 1)

    def test_register_one_item(self):
        """
        Test that when a single item is to be added to the tileindex
        a geomet_data_registry.tileindex.add() call is made.
        """

        # create sample item and append to base_layer.items
        item = self.create_item()
        self.base_layer.items.append(item)

        # assert that item registers and that tileindex.add() method
        # was called and tileindex.bulk_add() was not for a single item
        self.assertTrue(self.base_layer.register())
        self.mocked_load_plugin.return_value.add.assert_called_once()
        self.mocked_load_plugin.return_value.bulk_add.assert_not_called()

    def test_register_multiple_items(self):
        """
        Test that when multiple items are to be added to the tileindex
        a geomet_data_registry.tileindex.bulk_add() call is made.
        """

        # add 2 items in order to test multiple items registered
        item = self.create_item()
        self.base_layer.items.extend([item, item])

        # assert that items are registered and added to
        # tileindex via the tileindex.bulk_add() method
        self.assertTrue(self.base_layer.register())
        self.mocked_load_plugin.return_value.bulk_add.assert_called_once()


class TestLayer2Dict(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_gem_global', 'BaseLayer')

        # create item to be sent to layer2dict
        self.item = self.create_item()

        # expected return dict with above item
        self.expected_values = {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [-180, -90],
                        [-180, 90],
                        [180, 90],
                        [180, -90],
                        [-180, -90],
                    ]
                ],
            },
            'properties': {
                'identifier': 'GDPS.ETA_UGRD-20211126000000-20211128180000',
                'layer': 'GDPS.ETA_UGRD',
                'filepath': './geomet_data_registry/tests/data/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_UGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2',  # noqa
                'url': [None],
                'elevation': 'surface',
                'member': None,
                'model': 'model_gem_global',
                'weather_variable': [None],
                'reference_datetime': datetime(2021, 11, 26, 0, 0),
                'forecast_hour_datetime': datetime(2021, 11, 28, 18, 0),
                'receive_datetime': self.today_date,
                'identify_datetime': None,
                'register_datetime': None,
            },
        }

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()

    def test_layer2dict(self):

        # assert the return value from layer2dict is the expected dict above
        self.assertDictEqual(
            self.expected_values, self.base_layer.layer2dict(self.item)
        )

    def test_layer2dict_overwritten(self):

        # assert feature_dict property is overwritten if key found in
        # item dict when an item represents a UU layer for example
        # (multime wx_variables)
        self.expected_values['properties']['weather_variable'] = [
            'UGRD_TGL_10',
            'VGRD_TGL_10',
        ]
        self.item['weather_variable'] = ['UGRD_TGL_10', 'VGRD_TGL_10']
        self.assertDictEqual(
            self.expected_values, self.base_layer.layer2dict(self.item)
        )


class TestUpdateCount(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_gem_global', 'BaseLayer')

        # strings formatted with these would look like None_None_None otherwise
        # which makes it difficult to see whether or not it was done properly
        self.base_layer.model = 'model_gem_global'
        self.base_layer.wx_variable = 'TMP_TGL_2'
        self.base_layer.model_run = '00Z'
        self.base_layer.model_run_list = ['00Z', '12Z']
        self.item = self.create_item()

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()

    def test_update_count_expected_none(self):
        """
        Test that adding a new key to store is set to True when a new
        layer with no expected count is added (i.e radar data)
        """

        self.base_layer.update_count(self.item, 201)

        # assert new_key_store is True if r is 201 and expected count is None
        self.assertTrue(self.base_layer.new_key_store)

    def test_update_count_expected_81(self):
        """
        Test that count is initialized for a previously unencountered
        weather variable when a new file and an item has an expected count
        value.
        """

        # when store.get_key() is called, return None
        self.mocked_load_plugin.return_value.get_key.return_value = None

        # change expected count from None to 81 so it is greater than
        # new_layer_file_count
        self.item['expected_count'] = 81

        self.base_layer.update_count(self.item, 201)

        # assert new_key_store wasn't put to True and
        # store.set_key() was called using these parameters
        self.assertFalse(self.base_layer.new_key_store)
        self.mocked_load_plugin.return_value.set_key.assert_called_with(
            'model_gem_global_TMP_TGL_2_00Z_count', 1
        )

    def test_update_count_incomplete_mr(self):
        """
        Test that the appropriate model run count is reset when an imcomplete
        model run is identified and an error is logged.
        """

        # store.get_key() will return these values in sequence like a generator
        self.mocked_load_plugin.return_value.get_key.side_effect = [
            None,
            1,
            80,
        ]

        self.item['expected_count'] = 81

        # expected arguments used with store.set_key for the 2 calls
        calls = [
            call('model_gem_global_TMP_TGL_2_00Z_count', 1),
            call('model_gem_global_TMP_TGL_2_12Z_count', 0),
        ]

        with self.assertLogs(
            'geomet_data_registry.layer.base', level='ERROR'
        ) as err:
            self.base_layer.update_count(self.item, 201)
            # assert a single LOGGER.error was called
            self.assertEqual(len(err.records), 1)

        self.mocked_load_plugin.return_value.set_key.assert_has_calls(calls)

    def test_update_count_complete_mr(self):
        """
        Test that the appropriate model run counts are reset when a
        complete model run is achieved.
        """
        # make store.get_key return the same number as expected_count
        self.mocked_load_plugin.return_value.get_key.return_value = 80
        self.item['expected_count'] = 81

        self.base_layer.update_count(self.item, 201)

        # assert new_key_store was set to True
        self.assertTrue(self.base_layer.new_key_store)

        # assert these calls were made with store.set_key
        calls = [
            call('model_gem_global_TMP_TGL_2_00Z_count', 81),
            call('model_gem_global_TMP_TGL_2_00Z_count', 0),
            call('model_gem_global_TMP_TGL_2_12Z_count', 0),
        ]

        self.mocked_load_plugin.return_value.set_key.assert_has_calls(calls)


class TestCheckLayerDependencies(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_gem_global', 'BaseLayer')

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()

    def test_check_layer_dependencies(self):
        """
        Test geomet_data_registry.layer.BaseLayer.check_layer_dependencies()
        returns a list of dictionnaries representing tileindex items.
        """
        # make tileindex.get return an arbitrary
        # dict to assert that is what is returned
        self.mocked_load_plugin.return_value.get.return_value = {
            'geometry': {},
            'properties': {'weather_variable': 'VGRD_TGL_10'},
        }

        self.assertListEqual(
            self.base_layer.check_layer_dependencies(
                ['GDPS.ETA_VGRD'], '20211126000000', '20211126030000'
            ),
            [
                {
                    'geometry': {},
                    'properties': {'weather_variable': 'VGRD_TGL_10'},
                }
            ],
        )

    def test_check_layer_dependencies_tilenotfounderror(self):
        """
        Test geomet_data_registry.layer.BaseLayer.check_layer_dependencies()
        returns False when TileNotFoundError thrown when some dependencies
        are not found.
        """

        # make tileindex.get throw an error when called
        self.mocked_load_plugin.return_value.get.side_effect = (
            TileNotFoundError
        )

        # assert that False is returned when error is caught
        self.assertFalse(
            self.base_layer.check_layer_dependencies(
                ['GDPS.ETA_VGRD'], '20211126000000', '20211126030000'
            )
        )


class TestCheckDependenciesDefaultMr(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_gem_global', 'BaseLayer')

        self.dependencies = self.create_dependencies()
        self.mr_datetime = datetime.strptime(
            '2021-11-26T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'
        )

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()

    def test_check_dependencies_default_mr_nomatch(self):
        """
        Test that
        geomet_data_registry.layer.BaseLayer.check_dependencies_default_mr()
        returns False when no default model runs are found in the store
        for all layer dependencies (i.e when the layer dependencies
        haven't been processed yet by the registry).
        """
        # make default_mr return None, assert returns False
        self.mocked_load_plugin.return_value.get_key.return_value = None
        self.assertFalse(
            self.base_layer.check_dependencies_default_mr(
                self.mr_datetime, self.dependencies
            )
        )

    def test_check_dependencies_default_mr_matchall(self):
        """
        Test that
        geomet_data_registry.layer.BaseLayer.check_dependencies_default_mr()
        returns True when all layer dependencies model run datetimes
        match the passed datetime.
        """
        # make default_mr return same value as mr_datetime, assert returns True
        self.mocked_load_plugin.return_value.get_key.return_value = (
            '2021-11-26T00:00:00Z'
        )
        self.assertTrue(
            self.base_layer.check_dependencies_default_mr(
                self.mr_datetime, self.dependencies
            )
        )

    def test_check_dependencies_default_mr_halfmatch(self):
        """
        Test that
        geomet_data_registry.layer.BaseLayer.check_dependencies_default_mr()
        returns False when some dependencies model run datetimes
        match the passed datetime and some don't (i.e not all
        dependencies have been processed by the registry).
        """
        # make default_mr return these 2 values
        self.mocked_load_plugin.return_value.get_key.side_effect = [
            '2021-11-26T00:00:00Z',
            None,
        ]

        # assert if one of the values is False, return False
        self.assertFalse(
            self.base_layer.check_dependencies_default_mr(
                self.mr_datetime, self.dependencies
            )
        )


class TestAddTimeKey(unittest.TestCase, Setup):
    def setUp(self):
        """Code that executes before every test function."""

        Setup.__init__(self, 'model_gem_global', 'BaseLayer')

        self.check_dep_patcher = patch(
            'geomet_data_registry.layer.base.BaseLayer.check_dependencies_default_mr'  # noqa
        )
        self.mocked_check_dep_mr = self.check_dep_patcher.start()

        # create sample item, file_dict, model, items and date_ for base layer
        self.items = [
            {
                'elevation': '-1.6m',
                'expected_count': '49',
                'filepath': './geomet_data_registry/tests/data/model_riops/grib2/forecast/3d/2020/11/20201122T0Z_MSC_RIOPS_VOMECRTY_-1.6m_PS5km_P000.nc',  # noqa
                'forecast_hour_datetime': '2020-11-22T00:00:00Z',
                'forecast_hours': {'begin': 0, 'end': 48, 'interval': 'PT1H'},
                'identifier': (
                    'RIOPS_UU2W_Y_DBS-1.6m-20201122000000-20201122000000'
                ),
                'layer_config': {
                    'forecast_hours': '000/048/PT1H',
                    'dependencies': ['RIOPS_UU2W_X_DBS-1.6m'],
                },
                'layer_name': 'RIOPS_UU2W_Y_DBS-1.6m',
                'layer_name_unformatted': 'RIOPS_UU2W_Y_DBS-{}',
                'member': None,
                'model': 'model_riops_3D',
                'reference_datetime': '2020-11-22T00:00:00Z',
                'register_status': True,
            }
        ]

        self.base_layer.file_dict = {
            'model_riops': {
                'filename_pattern': '{YYYYMMDD_model_run}_MSC_RIOPS_{wx_variable}_{elevation}_PS5km_P{forecast_hour:n}.nc',  # noqa
                '3D': {
                    'variable': {
                        'VOMECRTY': {
                            'geomet_layers': {
                                'RIOPS_UU2W_Y_DBS-{}': {
                                    'forecast_hours': '000/048/PT1H',
                                    'dependencies': ['RIOPS_UU2W_X_DBS-{}'],
                                }
                            },
                            'model_run': {'00Z': {'files_expected': '49'}},
                            'members': 'null',
                            'bands': {
                                '2': {'product': '1.6m', 'elevation': '-1.6m'}
                            },
                            'bands_order': ['VOZOCRTX'],
                        }
                    }
                },
                'model_run_retention_hours': 120,
                'model_run_interval_hours': 12,
                'dimensions': {'x': '1800', 'y': '850'},
            }
        }
        self.base_layer.model = 'model_riops'
        self.base_layer.items = self.items
        self.base_layer.date_ = datetime(2020, 11, 22, 0, 0, 0)

    def tearDown(self):
        """Code that executes after every test function."""

        self.date_patcher.stop()
        self.plugin_patcher.stop()
        self.check_dep_patcher.stop()

    def test_add_time_key_no_match_deps(self):
        """
        Test that ensures no new time keys are set if item
        dependencies default model run is not identical
        to that of the current item.
        """

        # make store.get_key return a date < base_layer.date_
        self.mocked_load_plugin.return_value.get_key.return_value = (
            '2020-11-21T12:00:00Z'
        )

        # make check_dependencies_default_mr return False
        self.mocked_check_dep_mr.return_value = False

        # assert add_time_key was successful
        self.assertTrue(self.base_layer.add_time_key())

        # assert dependency does not match and store.set_key wasn't called
        expected_items = self.items
        expected_items[0]['refresh_config'] = False
        self.assertListEqual(expected_items, self.base_layer.items)
        self.mocked_load_plugin.return_value.set_key.assert_not_called()

    def test_add_time_key_older(self):
        """
        Test that ensures no new time keys are set if item currently
        being added would set default model run to an older value than
        the currently stored default model run.
        """

        # make store.get_key return a date > base_layer.date_
        self.mocked_load_plugin.return_value.get_key.return_value = (
            '2020-11-22T12:00:00Z'
        )

        # assert add_time_key was successful
        self.assertTrue(self.base_layer.add_time_key())

        # assert time keys not updated and new default model run
        # value is older than the current value in store
        expected_items = self.items
        self.assertListEqual(expected_items, self.base_layer.items)
        self.mocked_load_plugin.return_value.set_key.assert_not_called()

    def test_add_time_key_keys_set(self):
        """
        Test that new time keys are set if currently if item model run is
        more recent than the currently stored default model run and
        dependencies default model run values are identical.
        """
        # used for expected values for calls
        start_time = datetime(2020, 11, 22, 0, 0, 0) + timedelta(
            hours=self.items[0]['forecast_hours']['begin']
        )
        end_time = datetime(2020, 11, 22, 0, 0, 0) + timedelta(
            hours=self.items[0]['forecast_hours']['end']
        )
        start_time = start_time.strftime(DATE_FORMAT)
        end_time = end_time.strftime(DATE_FORMAT)
        run_start_time = (
            datetime(2020, 11, 22) - timedelta(hours=120)
        ).strftime(DATE_FORMAT)
        date_formatted = datetime(2020, 11, 22).strftime(DATE_FORMAT)

        # make check_dependencies_default_mr return True
        self.mocked_check_dep_mr.return_value = True

        # make store.get_key return a date < base_layer.date_
        self.mocked_load_plugin.return_value.get_key.return_value = (
            '2020-11-21T12:00:00Z'
        )

        # assert add_time_key was successful
        self.assertTrue(self.base_layer.add_time_key())

        # assert item values were not changed
        self.assertListEqual(self.items, self.base_layer.items)

        # assert store.set_key was called 3 times using these parameters
        calls = [
            call(
                'RIOPS_UU2W_Y_DBS-1.6m_time_extent',
                '{}/{}/PT1H'.format(start_time, end_time),
            ),
            call('RIOPS_UU2W_Y_DBS-1.6m_default_model_run', date_formatted),
            call(
                'RIOPS_UU2W_Y_DBS-1.6m_model_run_extent',
                '{}/{}/PT12H'.format(run_start_time, date_formatted),
            ),
        ]
        self.mocked_load_plugin.return_value.set_key.assert_has_calls(
            calls, any_order=True
        )


if __name__ == '__main__':
    unittest.main()
