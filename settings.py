#!/usr/bin/env python3
#
# Copyright (c) 2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#


# Settings class with common variables used in the quickstart scripts
class SimulatorSettings:
    # IP address of the endpoint running the Simulator. Default value is "127.0.0.1"
    simulator_host = "127.0.0.1"

    # Port used by the Simulator for the Python API connection. Default value is 8181
    simulator_port = 8181

    # IP address of the endpoint running the bridge. Default value is "127.0.0.1"
    bridge_host = "127.0.0.1"

    # Port used by the Simulator for the bridge connection. Default value is 9090
    bridge_port = 9090

    # Map loaded in the quickstart scripts. Changing the map may lead to unexpected behaviour in the quickstart scripts. Default value is "BorregasAve"
    # https://wise.svlsimulator.com/maps/profile/aae03d2a-b7ca-4a88-9e41-9035287a12cc
    map_borregasave = "aae03d2a-b7ca-4a88-9e41-9035287a12cc"

    # Ego vehicle that is loaded in most of the quickstart scripts. Default value is "Lincoln2017MKZ". This includes a bridge connection if needed and also bunch of sensors including LIDAR.
    # https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e/edit/configuration/47b529db-0593-4908-b3e7-4b24a32a0f70
    ego_lincoln2017mkz_apollo5 = "47b529db-0593-4908-b3e7-4b24a32a0f70"
