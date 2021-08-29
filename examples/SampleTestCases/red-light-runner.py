#!/usr/bin/env python3
#
# Copyright (c) 2019 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

# LGSVL__SIMULATOR_HOST and LGSVL__AUTOPILOT_0_HOST are environment variables
# They can be set for the terminal instance with `export LGSVL__SIMULATOR_HOST=###`
# which will use the set value for all future commands in that terminal.
# To set the variable for only a particular execution, run the script in this way
# `LGSVL__SIMULATOR_HOST=### LGSVL__AUTOPILOT_0_HOST=### python3 cut-in.py`

# LGSVL__SIMULATOR_HOST is the IP of the computer running the simulator
# LGSVL__AUTOPILOT_0_HOST is the IP of the computer running the bridge (from the perspective of the Simulator)
# If the simulator and bridge are running on the same computer, then the default values will work.
# Otherwise the variables must be set for in order to connect to the simulator and the bridge to receive data.
# LGSVL__SIMULATOR_PORT and LGSVL__AUTOPILOT_0_HOST need to be set if non-default ports will be used

import os
import lgsvl

import sys

SIMULATOR_HOST = os.environ.get("LGSVL__SIMULATOR_HOST", "127.0.0.1")
SIMULATOR_PORT = int(os.environ.get("LGSVL__SIMULATOR_PORT", 8181))
BRIDGE_HOST = os.environ.get("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
BRIDGE_PORT = int(os.environ.get("LGSVL__AUTOPILOT_0_PORT", 9090))

scene_name = os.environ.get("LGSVL__MAP", lgsvl.wise.DefaultAssets.map_borregasave)
sim = lgsvl.Simulator(SIMULATOR_HOST, SIMULATOR_PORT)
if sim.current_scene == scene_name:
    sim.reset()
else:
    sim.load(scene_name, seed=0)

# spawn EGO
egoState = lgsvl.AgentState()
egoState.transform = sim.get_spawn()[0]
ego = sim.add_agent(os.environ.get("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5_full_analysis), lgsvl.AgentType.EGO, egoState)
ego.connect_bridge(BRIDGE_HOST, BRIDGE_PORT)

forward = lgsvl.utils.transform_to_forward(egoState.transform) # Unit vector in the forward direction of the EGO
right = lgsvl.utils.transform_to_right(egoState.transform) # Unit vector in the right direction of the EGO

# spawn NPC
npcState = lgsvl.AgentState()
npcState.transform = sim.map_point_on_lane(egoState.position + 51.1 * forward + 29 * right) # NPC is 20m ahead of the EGO
npc = sim.add_agent("SUV", lgsvl.AgentType.NPC, npcState)

# This function will be called if a collision occurs
def on_collision(agent1, agent2, contact):
    raise Exception("{} collided with {}".format(agent1, agent2))

ego.on_collision(on_collision)
npc.on_collision(on_collision)

controlReceived = False

# This function will be called when the Simulator receives the first message on the topic defined in the CheckControlSensor configuration
def on_control_received(agent, kind, context):
    global controlReceived
    # There can be multiple custom callbacks defined, this checks for the appropriate kind
    if kind == "checkControl":
        # Stops the Simulator running, this will only interrupt the first sim.run(30) call
        sim.stop()
        controlReceived = True

ego.on_custom(on_control_received)

# Run Simulator for at most 30 seconds for the AD stack to to initialize
sim.run(30)

# If a Control message was not received, then the AD stack is not ready and the scenario should not continue
if not controlReceived:
    raise Exception("AD stack is not ready")
    sys.exit()

# Create the list of waypoints for the npc to follow
waypoints = []
# First waypoint is the same position that the npc is spawned. The npc will wait here until the EGO is within 50m
waypoints.append(lgsvl.DriveWaypoint(position=npcState.position, speed=20.1168, angle=npcState.rotation, idle=0, deactivate=False, trigger_distance=35))
# Second waypoint is across the intersection
endPoint = sim.map_point_on_lane(egoState.position + 51.1 * forward - 63.4 * right)
waypoints.append(lgsvl.DriveWaypoint(position=endPoint.position, speed=0, angle=endPoint.rotation))
npc.follow(waypoints)

# Set all the traffic lights to green.
# It is possible to set only the lights visible by the EGO to green, but positions of the lights must be known
signals = sim.get_controllables("signal")
for signal in signals:
    signal.control("green=3")

# Run the simulation for 30 seconds
sim.run(30)
