###############################################################################
#
# Copyright (C) 2018
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

import logging
import os

import click
import yaml

from geomet_weather.env import BASEDIR, CONFIG, DATADIR

LOGGER = logging.getLogger(__name__)

@click.command('expand-yml')
@click.pass_context
@click.option('--group', '-grp', help='group name')
def expand_yml(ctx, group):
    """expand yaml to write all the layers"""

    output_dir = '{}{}conf'.format(BASEDIR, os.sep)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

        yml_basedir = "{}/../conf/".format(BASEDIR)

        if group is not None:
            group_yml = 'geomet-weather_{}.yml'
            yml_file = os.path.join(yaml_basedir, group_yml)
            with open() as fh:
                cfg = yaml.load(fh)
        else:
            for group_yml in os.walk(yml_basedir):
                if group_yml.startswith('geomet-weather'):
                    with open(group_yml) as fh:
                        cfg = yml.load(fh)
