#!/bin/bash
# =================================================================
#
# Author: Tom Kralidis <tom.kralidis@canada.ca>
#
# Copyright (c) 2020 Tom Kralidis
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
geomet-data-registry store setup
geomet-data-registry tileindex setup

echo "Populating GDR store"
geomet-data-registry store set -k cansips -c /home/geoadm/geomet-data-registry/conf/cansips.yml
geomet-data-registry store set -k geps -c /home/geoadm/geomet-data-registry/conf/geps.yml
geomet-data-registry store set -k model_gem_global -c /home/geoadm/geomet-data-registry/conf/model_gem_global.yml
geomet-data-registry store set -k model_gem_regional -c /home/geoadm/geomet-data-registry/conf/model_gem_regional.yml
geomet-data-registry store set -k model_giops -c /home/geoadm/geomet-data-registry/conf/model_giops.yml
geomet-data-registry store set -k model_hrdps_continental -c /home/geoadm/geomet-data-registry/conf/model_hrdps_continental.yml
geomet-data-registry store set -k reps -c /home/geoadm/geomet-data-registry/conf/reps.yml
#geomet-data-registry store set -k radar -c /home/geoadm/geomet-data-registry/conf/radar.yml

echo "Starting data feeds"
sr_subscribe start /home/geoadm/geomet-data-registry/conf/sarracenia/cansips.conf
sr_subscribe start /home/geoadm/geomet-data-registry/conf/sarracenia/geps.conf
sr_subscribe start /home/geoadm/geomet-data-registry/conf/sarracenia/model_gem_global.conf
sr_subscribe start /home/geoadm/geomet-data-registry/conf/sarracenia/model_gem_regional.conf
sr_subscribe start /home/geoadm/geomet-data-registry/conf/sarracenia/model_giops.conf
sr_subscribe start /home/geoadm/geomet-data-registry/conf/sarracenia/model_hrdps_continental.conf
sr_subscribe start /home/geoadm/geomet-data-registry/conf/sarracenia/reps.conf
#sr_subscribe start /home/geoadm/geomet-data-registry/conf/sarracenia/radar.conf
