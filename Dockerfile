###############################################################################
#
# Copyright (C) 2021 Tom Kralidis
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

FROM python:3.6-slim-buster

ENV GDR_LOGGING_LOGLEVEL DEBUG
ENV GDR_LOGGING_LOGFILE /tmp/geomet-data-registry-dev.log
ENV GDR_CONFIG /opt/geomet-data-registry/geomet-data-registry.yml
ENV GDR_BASEDIR /home/geoadm/geomet-data-registry
ENV GDR_DATADIR /data/geomet/feeds
ENV GDR_TILEINDEX_TYPE Elasticsearch
ENV GDR_TILEINDEX_BASEURL http://localhost:9200
ENV GDR_TILEINDEX_NAME geomet-data-registry-nightly
ENV GDR_STORE_TYPE Redis
ENV GDR_STORE_URL redis://redis:6379
ENV GDR_METPX_DISCARD on
ENV GDR_METPX_EVENT_FILE_PY /home/geoadm/geomet-data-registry/geomet_data_registry/event/file_.py
ENV GDR_METPX_EVENT_MESSAGE_PY /home/geoadm/geomet-data-registry/geomet_data_registry/event/message.py
ENV GDR_METPX_NOTIFY True
ENV GDR_GEOMET_ONLY_USER username
ENV GDR_GEOMET_ONLY_PASS password
ENV GDR_GEOMET_ONLY_HOST feeds.example.org
ENV GDR_NOTIFICATIONS False
ENV GDR_NOTIFICATIONS_TYPE Celery
ENV GDR_NOTIFICATIONS_URL redis://localhost:6379
ENV XDG_CACHE_HOME /tmp/geomet-data-registry-sarra-logs

# install commonly used dependencies
RUN apt-get update \
  && apt-get install -y ca-certificates curl gcc locales make redis-tools sudo \
  && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen \
  && useradd -ms /bin/bash geoadm && echo "geoadm:geoadm" | chpasswd && adduser geoadm sudo \
  && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

WORKDIR /home/geoadm

# setup geomet-data-registry
USER geoadm
COPY . /home/geoadm/geomet-data-registry
WORKDIR /home/geoadm/geomet-data-registry
RUN sudo python setup.py install \
  && sudo mkdir -p ${GDR_DATADIR} \
  && sudo chown -R geoadm:geoadm ${GDR_DATADIR} \
  && mkdir -p ${XDG_CACHE_HOME}

ENTRYPOINT [ "/home/geoadm/geomet-data-registry/docker/entrypoint.sh" ]
