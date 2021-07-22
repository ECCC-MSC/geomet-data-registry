#!/bin/bash
# =================================================================
#
# Author: Tom Kralidis <tom.kralidis@canada.ca>
#
# Copyright (c) 2021 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

echo "Verifying GDR supporting services are available"
until curl --silent --output /dev/null --show-error --fail "$GDR_TILEINDEX_BASEURL" && redis-cli -u $GDR_STORE_URL ping; do
  >&2 echo "Elasticsearch or Redis is not unavailable - sleeping"
  sleep 1
done

>&2 echo "Elasticsearch and Redis are up - continuing"

echo "Setting up GDR store and tileindex"
#geomet-data-registry store setup
#geomet-data-registry tileindex setup


echo "Populating GDR store"
geomet-data-registry store set -k cansips -c /home/geoadm/geomet-data-registry/deploy/default/cansips.yml
geomet-data-registry store set -k cgsl -c /home/geoadm/geomet-data-registry/deploy/default/cgsl.yml
geomet-data-registry store set -k gdwps -c /home/geoadm/geomet-data-registry/deploy/default/gdwps.yml
geomet-data-registry store set -k geps -c /home/geoadm/geomet-data-registry/deploy/default/geps.yml
geomet-data-registry store set -k hrdpa -c /home/geoadm/geomet-data-registry/deploy/default/hrdpa.yml
geomet-data-registry store set -k model_gem_global -c /home/geoadm/geomet-data-registry/deploy/default/model_gem_global.yml
geomet-data-registry store set -k model_gem_regional -c /home/geoadm/geomet-data-registry/deploy/default/model_gem_regional.yml
geomet-data-registry store set -k model_giops -c /home/geoadm/geomet-data-registry/deploy/default/model_giops.yml
geomet-data-registry store set -k model_hrdps_continental -c /home/geoadm/geomet-data-registry/deploy/default/model_hrdps_continental.yml
geomet-data-registry store set -k model_raqdps-fw-ce -c /home/geoadm/geomet-data-registry/deploy/default/model_raqdps-fw-ce.yml
geomet-data-registry store set -k model_raqdps-fw -c /home/geoadm/geomet-data-registry/deploy/default/model_raqdps-fw.yml
geomet-data-registry store set -k model_raqdps -c /home/geoadm/geomet-data-registry/deploy/default/model_raqdps.yml
geomet-data-registry store set -k model_rdaqa-ce -c /home/geoadm/geomet-data-registry/deploy/default/model_rdaqa-ce.yml
geomet-data-registry store set -k model_riops -c /home/geoadm/geomet-data-registry/deploy/default/model_riops.yml
geomet-data-registry store set -k radar -c /home/geoadm/geomet-data-registry/deploy/default/radar.yml
geomet-data-registry store set -k rdpa -c /home/geoadm/geomet-data-registry/deploy/default/rdpa.yml
geomet-data-registry store set -k rdwps -c /home/geoadm/geomet-data-registry/deploy/default/rdwps.yml
geomet-data-registry store set -k reps -c /home/geoadm/geomet-data-registry/deploy/default/reps.yml
geomet-data-registry store set -k wcps -c /home/geoadm/geomet-data-registry/deploy/default/wcps.yml

echo "Starting data feeds"
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/cansips.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/cgsl.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/gdwps.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/geps.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/hrdpa.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/model_gem_global.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/model_gem_regional.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/model_giops.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/model_hrdps_continental.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/model_raqdps-fw-ce.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/model_raqdps-fw.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/model_raqdps.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/model_rdaqa-ce.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/model_riops.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/radar.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/rdpa.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/rdwps.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/reps.conf
sr_subscribe start /home/geoadm/geomet-data-registry/deploy/default/sarracenia/wcps.conf

sleep infinity
