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
import re

import click
import yaml

from geomet_weather.env import BASEDIR

LOGGER = logging.getLogger(__name__)


def write_yml(cfg, output_dir, group):

    layer_name = {}
    old_key = []

    yaml_file_out = os.path.join(output_dir,
                                 'geomet-weather-{}.yml'.format(group))

    for key in cfg['layers']:
        if 'PRES' in key:
            for levels in cfg['layers'][key]['pressure_levels']:
                tmp_ld = {}
                tmp_ld = cfg['layers'][key].copy()
                tmp_ld['label_en'] = tmp_ld['label_en'].format(levels,
                                                               levels)
                tmp_ld['label_fr'] = tmp_ld['label_fr'].format(levels,
                                                               levels)
                tmp_ld['name'] = tmp_ld['name'].format(levels)
                key_new = re.sub(r'\{.*}', '{}', key).format(levels)
                layer_name[key_new] = tmp_ld
                del layer_name[key_new]['pressure_levels']
            old_key.append(key)

    for i in old_key:
        del cfg['layers'][i]

    cfg['layers'].update(layer_name)

    with open(yaml_file_out, 'w', encoding='utf-8') as outfile:
        yaml.dump(cfg, outfile, default_flow_style=False, allow_unicode=True)
    print("hello world")


@click.command('expand-yml')
@click.pass_context
@click.option('--group', '-grp', help='group name')
def expand_yml(ctx, group):
    """expand yaml to write all the layers"""

    output_dir = '{}{}build{}conf'.format(BASEDIR, os.sep, os.sep)
    tmp_output_dir = '{}{}build{}tmp{}conf'.format(BASEDIR,
                                                   os.sep,
                                                   os.sep,
                                                   os.sep)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(tmp_output_dir):
        os.makedirs(tmp_output_dir)

    yml_basedir = "{}/conf/".format(BASEDIR)
    if group is not None:
        group_yml = 'geomet-weather_{}.yml'.format(group)
        yml_file = os.path.join(yml_basedir, group_yml)
        group_yml_file = os.path.join(tmp_output_dir, group_yml)
        template_file = os.path.join(yml_basedir, 'template.yml')

        with open(group_yml_file, 'w') as gyf:

            with open(template_file) as template:
                gyf.write(template.read())

            with open(yml_file) as fh:
                gyf.write(fh.read())

        with open(group_yml_file) as gyf:
            cfg = yaml.load(gyf)
            write_yml(cfg, output_dir, group)
    else:
        for group_yml in os.walk(yml_basedir):
            if group_yml.startswith('geomet-weather'):
                with open(group_yml) as fh:
                    cfg = yaml.load(fh)
