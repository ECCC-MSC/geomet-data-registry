###############################################################################
#
# Copyright (C) 2019 Tom Kralidis
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
FROM elasticsearch:latest
FROM redis:latest

# install commonly used dependencies

RUN apt-get update

RUN apt-get install -y locales

# Set the locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN useradd -ms /bin/bash geoadm

USER geoadm
WORKDIR /home/geoadm

EXPOSE 6379
EXPOSE 9200

# setup geomet-data-registry

RUN git clone https://gccode.ssc-spc.gc.ca/ec-msc/geomet-data-registry.git
WORKDIR geomet-data-registry
RUN python setup.py install
WORKDIR ..
