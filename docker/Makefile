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

IMAGE=geomet-weather-image
CONTAINER=geomet-weather-container
HOSTNAME=mandalor

DATA_VOLUME=/data/geomet

help:
	@echo
	@echo "make targets:"
	@echo " run: run container"
	@echo " build: build image"
	@echo " login: login to container"
	@echo " stop: stop container"
	@echo " clean: remove container"
	@echo

run:
	docker run --name $(CONTAINER) -d -i -t -v $(DATA_VOLUME):$(DATA_VOLUME) --hostname $(HOSTNAME) -p 8001:80 -p 9200:9200 -p 6379:6379 $(IMAGE)

build:
	docker build -t $(IMAGE) .

login:
	docker exec -it $(CONTAINER) /bin/bash

login-root:
	docker exec -u 0 -it $(CONTAINER) /bin/bash

stop:
	docker stop $(CONTAINER)

clean:
	docker rm -f $(CONTAINER)
	docker rmi $(IMAGE)

.PHONY: help run build login login-root stop clean
