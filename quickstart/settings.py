#!/usr/bin/env python3
#
# Copyright (c) 2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#


# Settings class with common variables used in the quickstart scripts
class SimulatorSettings:
	# IP address of the endpoint running the Simulator. Default value is "127.0.0.1"
	simulatorHost = "127.0.0.1"

	# Port used by the Simulator for the Python API connection. Default value is 8181
	simulatorPort = 8181

	# IP address of the endpoint running the bridge. Default value is "127.0.0.1"
	bridgeHost = "127.0.0.1"

	# Port used by the Simulator for the bridge connection. Default value is 9090
	bridgePort = 9090

	# Map loaded in the quickstart scripts. Changing the map may lead to unexpected behaviour in the quickstart scripts. Default value is "BorregasAve"
	mapName = "BorregasAve"

	# Ego vehicle that is loaded in most of the quickstart scripts. Default value is "Lincoln2017MKZ"
	egoVehicle = "Lincoln2017MKZ"

	# Ego vehicle that is loaded in quickstart scripts where the bridge connection is required. Default value is "Lincoln2017MKZ"
	egoVehicleWithBridge = "Lincoln2017MKZ"

	# Ego vehicle that is loaded in quickstart scripts where the LIDAR sensor is required. Default value is "Lincoln2017MKZ"
	egoVehicleWithLidar = "Lincoln2017MKZ"