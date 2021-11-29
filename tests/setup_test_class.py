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

from datetime import datetime, timezone
import importlib
import json
from unittest.mock import patch, DEFAULT


class Setup:
    def __init__(self, test_file, classname, handler_name=None):
        # if instance.name is not identical to file name, provide it
        self.handler_name = handler_name or test_file

        module = (
            importlib.import_module(f'geomet_data_registry.layer.{test_file}')
        )
        class_ = getattr(module, classname)

        self.date_patcher = patch(
            'geomet_data_registry.layer.base.get_today_and_now'
        )
        self.mocked_get_date = self.date_patcher.start()

        self.plugin_patcher = patch(
            'geomet_data_registry.layer.base.load_plugin'
        )
        self.mocked_load_plugin = self.plugin_patcher.start()

        self.maxDiff = None
        self.today_date = (
            datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        )
        self.mocked_get_date.return_value = self.today_date

        if 'BaseLayer' in repr(class_):
            # if we're testing base layer, send a real provider def, otherwise
            # send 'whatever' since it should be overridden by the real one
            self.base_layer = class_({'name': self.handler_name})
        else:
            # patch base layer init only when accessed with super().__init__()
            self.init_patcher = patch(
                f'geomet_data_registry.layer.{test_file}.BaseLayer.__init__'
            )
            self.mocked_base_init = self.init_patcher.start()

            self.layer_handler = {test_file: class_({'name': 'whatever'})}
            self.add_init_attr(self.layer_handler[test_file])

    def add_init_attr(self, instance):
        """Mocked BaseLayer instanciation"""

        instance.items = []
        instance.model_run_list = []

        instance.receive_datetime = self.today_date
        instance.identify_datetime = None
        instance.register_datetime = None
        instance.filepath = None
        instance.url = None
        instance.dimensions = None
        instance.model = None
        instance.model_run = None
        instance.geomet_layers = None
        instance.wx_variable = None
        instance.date_ = None
        instance.file_dict = None
        instance.new_key_store = False

        instance.name = self.handler_name
        instance.store = self.mocked_load_plugin.return_value
        instance.tileindex = self.mocked_load_plugin.return_value

    def create_item(self):
        """Returns a fake item."""

        return {
            'layer_name': 'GDPS.ETA_UGRD',
            'filepath': './geomet_data_registry/tests/data/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_UGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2',  # noqa
            'identifier': 'GDPS.ETA_UGRD-20211126000000-20211128180000',
            'reference_datetime': datetime(2021, 11, 26, 0, 0),
            'forecast_hour_datetime': datetime(2021, 11, 28, 18, 0),
            'member': None,
            'elevation': 'surface',
            'expected_count': None,
            'register_status': True,
            'model': 'model_gem_global',
        }

    def create_dependencies(self):
        """Return abitrary values to simulate dependencies."""

        return [
            {
                'properties': {
                    'filepath': './geomet_data_registry/tests/data/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_UGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2',  # noqa
                    'url': ['https://dd4.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_UGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2'],  # noqa
                    'weather_variable': ['UGRD_TGL_10'],
                }
            },
            {
                'properties': {
                    'filepath': './geomet_data_registry/tests/data/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_VGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2',  # noqa
                    'url': ['https://dd4.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/00/066/CMC_glb_VGRD_TGL_10_latlon.15x.15_2021112600_P066.grib2'],  # noqa
                    'weather_variable': ['VGRD_TGL_10'],
                }
            },
        ]

    def side_effect(self, *args, **kwargs):
        """Transforms dict into json inside layer handlers"""
        get_key = self.mocked_load_plugin.return_value.get_key.return_value
        if type(get_key) is dict:
            return json.dumps(get_key)
        return DEFAULT
