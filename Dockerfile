###############################################################################
#
# Copyright (C) 2020 Tom Kralidis
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

FROM python:3.6-slim

ENV GDR_LOGGING_LOGLEVEL DEBUG
ENV GDR_LOGGING_LOGFILE /tmp/geomet-data-registry-dev.log
ENV GDR_CONFIG /opt/geomet-data-registry/geomet-data-registry.yml
ENV GDR_BASEDIR /opt/geomet-data-registry
ENV GDR_DATADIR /data/geomet
ENV GDR_URL http://localhost/geomet-data-registry
ENV GDR_TILEINDEX_TYPE Elasticsearch
ENV GDR_TILEINDEX_BASEURL http://elasticsearch:9200
ENV GDR_TILEINDEX_NAME geomet-data-registry-tileindex-dev
ENV GDR_STORE_TYPE Redis
ENV GDR_STORE_URL redis://redis:6379
ENV XDG_CACHE_HOME /tmp/gdr-dev-logs

#ENV DEB_BUILD_PACKAGES="gcc libyaml-dev"

# install commonly used dependencies
RUN apt-get update \
  && apt-get install -y gcc ${DEB_BUILD_PACKAGES} locales sudo ca-certificates \
  && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen \
  && useradd -ms /bin/bash geoadm && echo "geoadm:geoadm" | chpasswd && adduser geoadm sudo \
  && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

WORKDIR /home/geoadm

# setup geomet-data-registry
COPY . /home/geoadm
RUN sudo python setup.py install \
  && apt-get remove -y ${DEB_BUILD_PACKAGES}
RUN find conf/sarracenia -type f -name "*.conf" | sudo xargs sed -i "s#/data/geomet/dev/apps/geomet-data-registry-dev/geomet-data-registry#/home/geoadm/geomet-data-registry#g"
