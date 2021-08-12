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
	
	geomet-data-registry store set -k cansips -c deploy/default/cansips.yml
	geomet-data-registry store set -k cgsl -c deploy/default/cgsl.yml
	geomet-data-registry store set -k gdwps -c deploy/default/gdwps.yml
	geomet-data-registry store set -k geps -c deploy/default/geps.yml
	geomet-data-registry store set -k hrdpa -c deploy/default/hrdpa.yml
	geomet-data-registry store set -k model_gem_global -c deploy/default/model_gem_global.yml
	geomet-data-registry store set -k model_gem_regional -c deploy/default/model_gem_regional.yml
	geomet-data-registry store set -k model_giops -c deploy/default/model_giops.yml
	geomet-data-registry store set -k model_hrdps_continental -c deploy/default/model_hrdps_continental.yml
	geomet-data-registry store set -k model_raqdps-fw-ce -c deploy/default/model_raqdps-fw-ce.yml
	geomet-data-registry store set -k model_raqdps-fw -c deploy/default/model_raqdps-fw.yml
	geomet-data-registry store set -k model_raqdps -c deploy/default/model_raqdps.yml
	geomet-data-registry store set -k model_rdaqa-ce -c deploy/default/model_rdaqa-ce.yml
	geomet-data-registry store set -k model_riops -c deploy/default/model_riops.yml
	#geomet-data-registry store set -k radar -c deploy/default/radar.yml
	geomet-data-registry store set -k rdpa -c deploy/default/rdpa.yml
	geomet-data-registry store set -k rdwps -c deploy/default/rdwps.yml
	geomet-data-registry store set -k reps -c deploy/default/reps.yml
	geomet-data-registry store set -k wcps -c deploy/default/wcps.yml
  
start:  
	sr_subscribe start deploy/default/sarracenia/cansips.conf
	sr_subscribe start deploy/default/sarracenia/cgsl.conf
	sr_subscribe start deploy/default/sarracenia/gdwps.conf
	sr_subscribe start deploy/default/sarracenia/geps.conf
	sr_subscribe start deploy/default/sarr acenia/hrdpa.conf
	sr_subscribe start deploy/default/sarracenia/model_gem_global.conf
	sr_subscribe start deploy/default/sarracenia/model_gem_regional.conf
	sr_subscribe start deploy/default/sarracenia/model_giops.conf
	sr_subscribe start deploy/default/sarracenia/model_hrdps_continental.conf
	sr_subscribe start deploy/default/sarracenia/model_raqdps-fw-ce.conf
	sr_subscribe start deploy/default/sarracenia/model_raqdps-fw.conf
	sr_subscribe start deploy/default/sarracenia/model_raqdps.conf
	sr_subscribe start deploy/default/sarracenia/model_rdaqa-ce.conf
	sr_subscribe start deploy/default/sarracenia/model_riops.conf
	#sr_subscribe start deploy/default/sarracenia/radar.conf
	sr_subscribe start deploy/default/sarracenia/rdpa.conf
	sr_subscribe start deploy/default/sarracenia/rdwps.conf
	sr_subscribe start deploy/default/sarracenia/reps.conf
	sr_subscribe start deploy/default/sarracenia/wcps.conf

stop:
	sr_subscribe stop deploy/default/sarracenia/cansips.conf
	sr_subscribe stop deploy/default/sarracenia/cgsl.conf
	sr_subscribe stop deploy/default/sarracenia/gdwps.conf
	sr_subscribe stop deploy/default/sarracenia/geps.conf
	sr_subscribe stop deploy/default/sarracenia/hrdpa.conf
	sr_subscribe stop deploy/default/sarracenia/model_gem_global.conf
	sr_subscribe stop deploy/default/sarracenia/model_gem_regional.conf
	sr_subscribe stop deploy/default/sarracenia/model_giops.conf
	sr_subscribe stop deploy/default/sarracenia/model_hrdps_continental.conf
	sr_subscribe stop deploy/default/sarracenia/model_raqdps-fw-ce.conf
	sr_subscribe stop deploy/default/sarracenia/model_raqdps-fw.conf
	sr_subscribe stop deploy/default/sarracenia/model_raqdps.conf
	sr_subscribe stop deploy/default/sarracenia/model_rdaqa-ce.conf
	sr_subscribe stop deploy/default/sarracenia/model_riops.conf
	#sr_subscribe stop deploy/default/sarracenia/radar.conf
	sr_subscribe stop deploy/default/sarracenia/rdpa.conf
	sr_subscribe stop deploy/default/sarracenia/rdwps.conf
	sr_subscribe stop deploy/default/sarracenia/reps.conf
	sr_subscribe stop deploy/default/sarracenia/wcps.conf
	
.PHONY: clean clean-logs flake8 setup start stop
