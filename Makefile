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

BASEDIR= $(shell pwd)

foo:
	@echo $(BASEDIR)

clean: stop
	geomet-data-registry store teardown
	geomet-data-registry tileindex teardown

clean-logs:
	rm -fr $(XDG_CACHE_HOME)/*

flake8:
	find . -type f -name "*.py" | xargs flake8

setup:
	geomet-data-registry store setup
	geomet-data-registry tileindex setup
	
	geomet-data-registry store set -k cansips -c conf/cansips.yml
	geomet-data-registry store set -k geps -c conf/geps.yml
	geomet-data-registry store set -k model_gem_global -c conf/model_gem_global.yml
	geomet-data-registry store set -k model_gem_regional -c conf/model_gem_regional.yml
	geomet-data-registry store set -k model_giops -c conf/model_giops.yml
	geomet-data-registry store set -k model_hrdps_continental -c conf/model_hrdps_continental.yml
	geomet-data-registry store set -k reps -c conf/reps.yml
	#geomet-data-registry store set -k radar -c try/conf/radar.yml
	
start:
	sr_subscribe start conf/sarracenia/cansips.conf
	sr_subscribe start conf/sarracenia/geps.conf
	sr_subscribe start conf/sarracenia/model_gem_global.conf
	sr_subscribe start conf/sarracenia/model_gem_regional.conf
	sr_subscribe start conf/sarracenia/model_giops.conf
	sr_subscribe start conf/sarracenia/model_hrdps_continental.conf
	sr_subscribe start conf/sarracenia/reps.conf
	#sr_subscribe start msc-geomet-data-registry/conf/sarracenia/radar.conf
	
stop:
	sr_subscribe stop conf/sarracenia/cansips.conf
	sr_subscribe stop conf/sarracenia/geps.conf
	sr_subscribe stop conf/sarracenia/model_gem_global.conf
	sr_subscribe stop conf/sarracenia/model_gem_regional.conf
	sr_subscribe stop conf/sarracenia/model_giops.conf
	sr_subscribe stop conf/sarracenia/model_hrdps_continental.conf
	sr_subscribe stop conf/sarracenia/reps.conf
	#sr_subscribe stop msc-geomet-data-registry/conf/sarracenia/radar.conf
	
.PHONY: clean clean-logs flake8 setup start stop
