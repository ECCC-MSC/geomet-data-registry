###############################################################################
#
# Copyright (C) 2019 Louis-Philippe Rousseau-Lambert
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

import datetime
import io
import json
import mock
import os
import unittest

from yaml import load, Loader

from geomet_data_registry.layer.model_gem_global import (ModelGemGlobalLayer)


THISDIR = './geomet_data_registry/tests/'


def msg(test_id, test_description):
    """convenience function to print out test id and desc"""
    return '{}: {}'.format(test_id, test_description)


class Store():
    """To avoid using a redis store for th unit tests
       This way we mimic the store function and simply use the yamls"""

    yml_dir = os.path.join(THISDIR, 'conf')

    def get_key(self, model):
        """"""

        dict_yml_model = {'model_gem_global': 'model_gem_global-test.yml'}

        yml_file = os.path.join(self.yml_dir, dict_yml_model[model])
        with io.open(yml_file) as fh:
            cfg = json.dumps(load(fh, Loader=Loader))

        return cfg


class GeoMetDataRegistryTest(unittest.TestCase):
    """Test suite for package geomet-data-registry"""

    data_dir = os.path.join(THISDIR, 'data')
    yml_dir = os.path.join(THISDIR, 'conf')

    mock.patch('os.environ', {'BASEDIR': THISDIR,
                              'DATADIR': data_dir})

    def setUp(self):
        """setup test fixtures, etc."""

        print(msg(self.id(), self.shortDescription()))

    def tearDown(self):
        """return to pristine state"""

        pass

    def test_ModelGemGlobalLayer_identify(self):
        """Test the identify function for GDPS"""

        self.items = []
        self.store = Store()

        filedir = 'model_gem_global/25km/grib2/lat_lon/00/006'
        filename = 'CMC_glb_TMP_TGL_2_latlon.24x.24_2019080100_P006.grib2'
        filepath = os.path.join(self.data_dir, filedir, filename)

        item_result = [{'layer_name': 'GDPS.ETA_TT',
                       'filepath': './geomet_data_registry/tests/data/model_gem_global/25km/grib2/lat_lon/00/006/CMC_glb_TMP_TGL_2_latlon.24x.24_2019080100_P006.grib2', # noqa
                       'identifier': 'GDPS.ETA_TT-20190801000000-20190801060000', # noqa
                       'reference_datetime': datetime.datetime(2019, 8, 1, 0, 0), # noqa
                       'forecast_hour_datetime': datetime.datetime(2019, 8, 1, 6, 0), # noqa
                       'member': None,
                       'elevation': '2m',
                       'expected_count': 81}]

        result = ModelGemGlobalLayer.identify(self, filepath)

        self.assertIs(result, True)
        self.assertEqual(item_result, self.items)


if __name__ == '__main__':
    unittest.main()
