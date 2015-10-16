# plumerise

This package provides a module for computing plume rise from time-profiled
emissions output.

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

Then, to install, for example, v0.1.1, use the following (with sudo if necessary):

    pip install --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple plumerise==v0.1.1

If you get an error like

    AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex

it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip

## Usage

TODO: ...Fill in...
