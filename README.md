# geomet-weather

## Overview

geomet-weather provides the MapServer setup and configuration for deployment
of MSC GeoMet weather service data OGC Web Services.

## Installation

### Dependencies

- Python MapScript
- GDAL Python bindings

### Requirements
- Python 3
- [virtualenv](https://virtualenv.pypa.io/)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during installation.

### Installing geomet-weather
```bash

# install system wide packages
sudo apt-get install python-mapscript python-gdal

# setup virtualenv
python -m venv geomet-weather
cd geomet-weather
. bin/activate

# clone codebase and install
git clone https://gccode.ssc-spc.gc.ca/ec-msc/geomet-weather.git
cd geomet-weather
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

# configure environment
vi geomet-weather.env  # edit paths accordingly
. geomet-weather.env
```

## Running

```bash
# help
geomet-weather --help

# get version
geomet-weather --version

# generate VRTs for all layers
geomet-weather vrt generate

# generate VRTs for single group
geomet-weather vrt generate --group=GDPS

# generate tileindex for all layers/groups
geomet-weather tileindex generate

# generate tileindex for single group
geomet-weather tileindex generate --group=GDPS

# generate mapfile for WMS (English)
geomet-weather mapfile generate --language=en --service=WMS

# generate mapfile for WMS (English) with specific configuration for single layer
geomet-weather mapfile generate --language=en --service=WMS --layer=CMIP5.SND.RCP26.FALL.ANO_PCTL50

# generate mapfile for WMS (English) with specific configuration for single group
geomet-weather mapfile generate --language=en --service=WMS --group=GDPS

# generate mapfile for WCS (French)
geomet-weather mapfile generate --language=fr --service=WCS

# update mapfile
geomet-weather mapfile update --layer=GDPS.ETA_TT
geomet-weather mapfile update --group=GDPS --timedefault=YYYY-MM-DDTHH:MM:SSZ --timeextent=YYYY-MM-DDTHH:MM:SSZ/YYYY-MM-DDTHH:MM:SSZ/interval

# run server
geomet-weather serve  # server runs on port 8099

# run server on a different port
geomet-weather serve  --port=8011

# cache WMS and WCS Capabilities URLs
geomet-weather cache-ows-urls
```

## Development

### Running Tests

TODO

## Releasing

```bash
python setup.py sdist bdist_wheel --universal
twine upload dist/*
```

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues are managed on [GCcode](https://gccode.ssc-spc.gc.ca/ec-msc/geomet-weather).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)

