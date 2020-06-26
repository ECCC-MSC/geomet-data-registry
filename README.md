# geomet-data-registry

## Overview

geomet-data-registry provides the MapServer setup and configuration for deployment
of MSC GeoMet weather service data OGC Web Services.

## Installation

### Requirements
- Python 3
- [virtualenv](https://virtualenv.pypa.io/)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during installation.

### Installing geomet-data-registry
```bash

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

# setup tileindex
geomet-data-registry tileindex setup

# teardown tileindex
geomet-data-registry tileindex teardown

# setup store
geomet-data-registry store setup

# list all store keys
geomet-data-registry store list

# list all store keys filtering on a regex
geomet-data-registry store list --pattern="RADAR*"

# list all store keys filtering on a fancier regex
geomet-data-registry store list --pattern="RADAR*time$"

# teardown store
geomet-data-registry store teardown

# set key/value in store
geomet-data-registry store set --key=somekey --config=/path/to/file

# setup metadata
geomet-data-registry metadata setup

# start up
sr_subscribe path/to/amqp.conf foreground

# dev workflows
# process a test file
geomet-data-registry data add --file=/path/to/file

# dev workflows
# process a test directory of files (recursive)
geomet-data-registry data add --directory=/path/to/directory
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
