# lgsvl - A Python API for SVL Simulator

This folder contains **lgsvl**, a Python API for SVL Simulator.

# Usage

Look into `quickstart` and `examples` folders for simple usages. To run these
examples, first add the maps and vehicles they use into your Library, and then
launch a simulation on a local cluster selecting the **API Only** template.

By default, the examples expect to be able to connect to SVL Simulator using the
`localhost` address. To change it, set the `LGSVL__SIMULATOR_HOST` environment
variable to the hostname or IP address of the network interface of the machine
running SVL Simulator to which the examples should connect.

# Documentation

Documentation is available on our website: https://www.svlsimulator.com/docs/python-api/

# Requirements

* Python 3.6 or higher

# Installing

    pip3 install --user .

    # install in development mode
    pip3 install --user -e .

# Running unit tests

To run the unit tests, first add the maps and vehicles they use into your
Library, then launch a simulation on a local cluster selecting the **API Only**
template.

    # run all unittests
    python3 -m unittest discover -v -c

    # run single test module
    python3 -m unittest -v -c tests/test_XXXX.py

    # run individual test case
    python3 -m unittest -v tests.test_XXX.TestCaseXXX.test_XXX
    python3 -m unittest -v tests.test_Simulator.TestSimulator.test_unload_scene

# Creating test coverage report

    # (one time only) install coverage.py
    pip3 install --user coverage

    # run all tests with coverage
    ~/.local/bin/coverage run -m unittest discover

    # generate html report
    ~/.local/bin/coverage html --omit "~/.local/*","tests/*"

    # output is in htmlcov/index.html

# Copyright and License

Copyright (c) 2018-2021 LG Electronics, Inc.

This software contains code licensed as described in LICENSE.
