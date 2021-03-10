# lgsvl - A Python API for SVL Simulator

This folder contains **lgsvl**, a Python API for SVL Simulator.

# Documentation

Documentation is available on our website: https://www.svlsimulator.com/docs/python-api/

# Requirements

* Python 3.6 or higher

# Installing

    pip3 install --user .

    # install in development mode
    pip3 install --user -e .

# Examples

Look into `quickstart` and `examples` folders for simple usages. To run these
examples, first make sure that these assets have been added to your Library:

| Type    | Name           | URL |
| ------- | -------------- | --- |
| Map     | BorregasAve    | https://wise.svlsimulator.com/maps/profile/aae03d2a-b7ca-4a88-9e41-9035287a12cc |
| Map     | CubeTown       | https://wise.svlsimulator.com/maps/profile/06773677-1ce3-492f-9fe2-b3147e126e27 |
| Map     | SanFrancisco   | https://wise.svlsimulator.com/maps/profile/5d272540-f689-4355-83c7-03bf11b6865f |
| Map     | SingleLaneRoad | https://wise.svlsimulator.com/maps/profile/a6e2d149-6a18-4b83-9029-4411d7b2e69a |
| Map     | Straight1LanePedestrianCrosswalk | https://wise.svlsimulator.com/maps/profile/a3a818b5-c66b-488a-a780-979bd5692db1 |
| Map     | Straight1LaneSame | https://wise.svlsimulator.com/maps/profile/1e2287cf-c590-4804-bcb1-18b2fd3752d1 |
| Map     | Straight2LaneOpposing | https://wise.svlsimulator.com/maps/profile/671868be-44f9-44a1-913c-cb0f29d12634 |
| Map     | Straight2LaneSame | https://wise.svlsimulator.com/maps/profile/b39d3ef9-21d7-409d-851b-4c90dad80a25 |
| Map     | Straight2LaneSameCurbRightIntersection | https://wise.svlsimulator.com/maps/profile/378edc3f-8fce-4596-87dc-7d12fc2ad743 |
| Vehicle | Jaguar2015XE   | https://wise.svlsimulator.com/vehicles/profile/3f4211dc-e5d7-42dc-94c5-c4832b1331bb |
| Vehicle | Lincoln2017MKZ | https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e |

<br/>
and that the plugins required by these vehicle sensor configurations have been added to your Library:

| Vehicle      | Sensor Configuration | URL |
| ------------ | -------------------- | --- |
Jaguar2015XE   | Apollo 5.0           | https://wise.svlsimulator.com/vehicles/profile/3f4211dc-e5d7-42dc-94c5-c4832b1331bb/edit/configuration/c06d4932-5928-4730-8a91-ba64ac5f1813 |
Jaguar2015XE   | Autoware AI          | https://wise.svlsimulator.com/vehicles/profile/3f4211dc-e5d7-42dc-94c5-c4832b1331bb/edit/configuration/05cbb194-d095-4a0e-ae66-ff56c331ca83 |
Lincoln2017MKZ | Apollo 5.0           | https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e/edit/configuration/47b529db-0593-4908-b3e7-4b24a32a0f70 |
Lincoln2017MKZ | Apollo 5.0 (Full Analysis) | https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e/edit/configuration/22656c7b-104b-4e6a-9c70-9955b6582220 |
Lincoln2017MKZ | Apollo 5.0 (modular testing) | https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e/edit/configuration/5c7fb3b0-1fd4-4943-8347-f73a05749718 |
<br/>

Then launch a simulation on a local cluster selecting the **API Only** template.

By default, the examples expect to be able to connect to SVL Simulator using the
`localhost` address. To change it, set the `LGSVL__SIMULATOR_HOST` environment
variable to the hostname or IP address of the network interface of the machine
running SVL Simulator to which the examples should connect.


# Running unit tests

To run the unit tests, first make sure that these assets have been added to your Library:

| Type    | Name           | URL |
| ------- | -------------- | --- |
| Map     | BorregasAve    | https://wise.svlsimulator.com/maps/profile/aae03d2a-b7ca-4a88-9e41-9035287a12cc |
| Map     | CubeTown       | https://wise.svlsimulator.com/maps/profile/06773677-1ce3-492f-9fe2-b3147e126e27 |
| Vehicle | Jaguar2015XE   | https://wise.svlsimulator.com/vehicles/profile/3f4211dc-e5d7-42dc-94c5-c4832b1331bb |
| Vehicle | Lincoln2017MKZ | https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e |

<br/>
and that the plugins required by these vehicle sensor configurations have been added to your Library:

| Vehicle      | Sensor Configuration | URL |
| ------------ | -------------------- | --- |
Jaguar2015XE   | Apollo 5.0           | https://wise.svlsimulator.com/vehicles/profile/3f4211dc-e5d7-42dc-94c5-c4832b1331bb/edit/configuration/c06d4932-5928-4730-8a91-ba64ac5f1813 |
Jaguar2015XE   | Autoware AI          | https://wise.svlsimulator.com/vehicles/profile/3f4211dc-e5d7-42dc-94c5-c4832b1331bb/edit/configuration/05cbb194-d095-4a0e-ae66-ff56c331ca83 |
Lincoln2017MKZ | Apollo 5.0           | https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e/edit/configuration/47b529db-0593-4908-b3e7-4b24a32a0f70 |

<br/>
Then launch an **API Only** simulation before running the unit tests.

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
