# geomet-data-registry

## Overview

geomet-data-registry provides the MapServer setup and configuration for deployment
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

### Installing geomet-data-registry
```bash

# install system wide packages
sudo apt-get install python-mapscript python-gdal

# setup virtualenv
python -m venv geomet-data-registry
cd geomet-data-registry
. bin/activate

# clone codebase and install
git clone https://github.com/ECCC-MSC/geomet-data-registry.git
cd geomet-data-registry
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

# configure environment
cp geomet-data-registry.env dev.env
vi dev.env # edit paths accordingly
. dev.env
```

## Running

```bash
# help
geomet-data-registry --help

# get version
geomet-data-registry --version

# Expand yaml for all groups
geomet-data-registry expand-yml

# Expand yaml for single group
geomet-data-registry expand-yml --group=GDPS

# generate VRTs for all layers
geomet-data-registry vrt generate

# generate VRTs for single group
geomet-data-registry vrt generate --group=GDPS

# generate tileindex for all layers/groups
geomet-data-registry tileindex generate

# generate tileindex for single group
geomet-data-registry tileindex generate --group=GDPS

# generate mapfile for WMS (English)
geomet-data-registry mapfile generate --language=en --service=WMS

# generate mapfile for WMS (English) with specific configuration for single layer
geomet-data-registry mapfile generate --language=en --service=WMS --layer=GDPS.ETA_TT

# generate mapfile for WMS (English) with specific configuration for single group
geomet-data-registry mapfile generate --language=en --service=WMS --group=GDPS

# generate mapfile for WCS (French)
geomet-data-registry mapfile generate --language=fr --service=WCS

# update mapfile
geomet-data-registry mapfile update --layer=GDPS.ETA_TT
geomet-data-registry mapfile update --group=GDPS --timedefault=YYYY-MM-DDTHH:MM:SSZ --timeextent=YYYY-MM-DDTHH:MM:SSZ/YYYY-MM-DDTHH:MM:SSZ/interval

# run server
geomet-data-registry serve  # server runs on port 8099

# run server on a different port
geomet-data-registry serve  --port=8011

# cache WMS and WCS Capabilities URLs
geomet-data-registry cache-ows-urls
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

All bugs, enhancements and issues are managed on [GitHub](https://github.com/ECCC-MSC/geomet-data-registry).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)

