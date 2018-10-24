# TO BE UPDATED

# GeoMet

## Overview

The [MSC GeoMet](https://www.canada.ca/en/environment-climate-change/services/weather-general-tools-resources/weather-tools-specialized-data/geospatial-web-services.html) project seeks to serve meteorological data to Canadians using common and interoperable geospatial web services and formats.

Geospatial Web Services enable MSC to provide geospatially referenced data over the Internet. Users can easily and directly access meteorological data using their own tools. Specialized users as well as the general public can then easily access and display meteorological data (weather, radar, etc.) via simple and accessible tools such as web applications, desktop applications (such as Google Earth), mobile devices, expert tools (ArcGIS, QGIS and AutoCAD) and domain specific tools (NinJo, SPI, etc.). 

GeoMet is a project from Environment and Climate Change Canada / Meteorological Service of Canada in collaboration with Shared Services Canada to serve weather data via geospatial web services. Details of the project are found on https://wiki.cmc.ec.gc.ca/wiki/GeoMet

Presentations of MSC GeoMet are [available on this ECCC wiki](https://wiki.cmc.ec.gc.ca/wiki/GeoMet/Presentations#Current_presentations).

The scope of this repository is to host source code, code documentation and software issues pertaining to GeoMet. In addition to the [GCcode issues](https://gccode.ssc-spc.gc.ca/ec-msc/geomet/issues/) for this project, there's an [issue tracker for items related to GeoMet's data inputs](http://bugzilla.cmc.ec.gc.ca/buglist.cgi?query_format=specific&order=relevance%20desc&bug_status=__open__&product=GeoMet-2&list_id=21766) and a [wiki](https://wiki.cmc.ec.gc.ca/wiki/GeoMet) for documentation].

## Architecture

### MapServer

The server is deployed using [MapServer](http://mapserver.org).  MapServer is an ANSI C application which operates in a FastCGI or CGI environment. MapServer runs against 'mapfiles', text-based configuration files which configure data connections, symbolization, filters, metadata, etc.  Mapfiles are always processed at runtime (i.e. every HTTP request).

```
                          mapfile
                             | 
                             v
HTTP request -> mapserv CGI/FastCGI / MapScript -> HTTP response (map, XML)
```

### MapScript

Python MapScript is used as a wrapper to the MapServer library which allows custom scripting to MapServer's request/response design pattern.

## Installation

### MapServer via UbuntuGIS PPA

The most straightforward way of installing MapServer is via the UbuntuGIS PPA:

```bash
sudo apt-get install python-software-properties
sudo add-apt-repository ppa:ubuntugis/ppa
```
More information is available at https://wiki.ubuntu.com/UbuntuGIS

### Requirements

See `debian/control`

### Dependencies

See `requirements.txt`

### Installing the Package

```bash
python3 -m venv geomet-venv --system-site-packages
cd geomet-venv
source bin/activate
git clone https://gccode.ssc-spc.gc.ca/ec-msc/geomet.git
cd geomet
pip install ./geometpy
make all
```

This will install geomet into `/opt/geomet` by default.  Override the Makefile `BASEDIR` variable to install elsewhere.

GeoMet should now be available at

`http://localhost/geomet`

Sample endpoints:

* WMS: `http://localhost/geomet?service=WMS&version=1.3.0&request=GetCapabilities`
* WFS: `http://localhost/geomet?service=WFS&version=1.1.0&request=GetCapabilities`

## Contributing

To contribute to MSC GeoMet, please [fork](https://gccode.ssc-spc.gc.ca/ec-msc/geomet/fork/new) GeoMet and clone locally to begin development.  Sample workflow:

### Setting up a Development Environment

```bash
# setup a virtualenv
# IMPORTANT : --system-site-packages ensures all system Python libraries, e.g. mapscript, are carried along in the new virtualenv
python3 -m venv geomet-my-fork --system-site-packages && cd geomet-my-fork
source ./bin/activate
# clone the repository locally
git clone https://gccode.ssc-spc.gc.ca/USERNAME/geomet.git
cd geomet
# install Python dependencies
pip install -r requirements.txt
# install dev dependencies
pip install -r requirements-dev.txt
# add the main geomet master branch to keep up to date with upstream changes
git remote add upstream https://gccode.ssc-spc.gc.ca/ec-msc/geomet.git
git pull upstream master
# build GeoMet
make BASEDIR=`pwd`/build OWS_URL=http://localhost/geomet
# hook build configuration into Apache via Include directive:
# Include /path/to/geomet-my-fork/geomet/build/etc/apache2/geomet.conf
sudo /etc/init.d/apache2 graceful
```

### Configuring an AMQP backend

```bash
vi Makefile
# edit DATADIR accordingly
make amqp
# setup cleanup cronjob
crontab build/etc/cron.d/geomet
# subscribe to datamart updates
# start sr_subscribe listener
sr_subscribe --no 1 build/etc/amqp.dd-ops.conf start
# stop sr_subscribe listener
sr_subscribe --no 1 build/etc/amqp.dd-ops.conf stop
```

### Contributions

Contributions to GeoMet can be made via `<GC/Code>` Merge Requests.  Below is a sample contribution workflow from a GeoMet fork:

```bash
# create a local branch off master
# The name of the branch should include the issue number if it exists
git branch issue-72
git checkout issue-72
#
# make code/doc changes
#
git commit -am 'fix xyz (#72)'
git push origin issue-72
#
# submit GCcode merge request
```

### Tagging a Release

Tagging a release:

1. Ensure code is up to date (master / branch)
2. Update `VERSION.txt` and `debian/changelog`
4. Commit changes:
 - `git commit -m 'tagging release x.y.z' VERSION.txt debian/changelog`
5. push to the main repository
 - `git push origin master`
5. Tag the version
 - `git tag -a x.y.z -m 'tagging release x.y.z`
 - `git push --tags`


## Running tests

### Integration Testing

```bash
python tests/integration.py <url> --mapfile=path/to/mapfile
```

### Load Testing
```bash
bash -f tests/load.sh <url> requests.txt <requests> <concurrency>"
```

## Code Conventions

- Python
 - [PEP8](https://www.python.org/dev/peps/pep-0008)
 - 4 spaces, no tabs
 - always run code through flake8
 - did we mention 4 spaces, no tabs?
- MapServer
 - 1 space, no tabs
 - double quotes, not single quotes
 - static mapfile comments are always `##`, not `#`

## Bugs and Issues

All bugs, enhancements and issues can be logged on SSC GCcode at https://gccode.ssc-spc.gc.ca/ec-msc/geomet/issues
