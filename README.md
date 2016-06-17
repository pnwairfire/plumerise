# plumerise

This package provides a module for computing plume rise from time-profiled
emissions output.

***This software is provided for research purposes only. It's output may
not accurately reflect observed data due to numerous reasons. Data are
provisional; use at own risk.***


## Python 2 and 3 Support

This package was originally developed to support python 2.7, but has since
been refactored to support 3.5. Attempts to support both 2.7 and 3.5 have
been made but are not guaranteed.

## Non-python Dependencies

### FEPS

If running FEPS plumerise, you'll need the feps_weather and feps_plumerise
executables. They are expected to reside in a directory in the search path.
Contact [USFS PNW AirFire Research Team](http://www.airfire.org/) for more
information.

## Development

Via ssh:

    git clone git@github.com:pnwairfire/plumerise.git

or http:

    git clone https://github.com/pnwairfire/plumerise.git

### Install Dependencies

Run the following to install dependencies:

    pip install -r requirements.txt

Run the following to install packages required for development and testing:

    pip install -r requirements-test.txt
    pip install -r requirements-dev.txt

### Setup Environment

To import plumerise in development, you'll have to add the repo root directory
to the search path.

## Running tests

Use pytest:

    py.test

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

See [pytest](http://pytest.org/latest/getting-started.html#getstarted) for more information about

## Installing

### Installing With pip

First, install pip (with sudo if necessary):

    apt-get install python-pip

Then, to install, for example, v0.2.1, use the following (with sudo if necessary):

    pip install --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple plumerise==v0.2.1

If you get an error like

    AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex

it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip

## Usage

TODO: ...Fill in...
