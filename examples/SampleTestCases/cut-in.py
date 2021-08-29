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

import time
import sys

SIMULATOR_HOST = os.environ.get("LGSVL__SIMULATOR_HOST", "127.0.0.1")
SIMULATOR_PORT = int(os.environ.get("LGSVL__SIMULATOR_PORT", 8181))
BRIDGE_HOST = os.environ.get("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
BRIDGE_PORT = int(os.environ.get("LGSVL__AUTOPILOT_0_PORT", 9090))

scene_name = os.environ.get("LGSVL__MAP", lgsvl.wise.DefaultAssets.map_sanfrancisco)

sim = lgsvl.Simulator(SIMULATOR_HOST, SIMULATOR_PORT)
if sim.current_scene == scene_name:
    sim.reset()
else:
    sim.load(scene_name, seed=0)

# spawn EGO
egoState = lgsvl.AgentState()
# Spawn point found in Unity Editor
egoState.transform = sim.map_point_on_lane(lgsvl.Vector(773.29, 10.24, -10.79))
ego = sim.add_agent(os.environ.get("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5_full_analysis), lgsvl.AgentType.EGO, egoState)
ego.connect_bridge(BRIDGE_HOST, BRIDGE_PORT)

right = lgsvl.utils.transform_to_right(egoState.transform) # Unit vector in the right direction of the EGO
forward = lgsvl.utils.transform_to_forward(egoState.transform) # Unit vector in the forward direction of the EGO

# spawn NPC
npcState = lgsvl.AgentState()
npcState.transform = egoState.transform
npcState.transform.position = egoState.position - 3.6 * right # NPC is 3.6m to the left of the EGO
npc = sim.add_agent("Jeep", lgsvl.AgentType.NPC, npcState)

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
    raise Exception("AD stack is not ready after 30 seconds")
    sys.exit()

# NPC will follow the HD map at a max speed of 15 m/s (33 mph) and will not change lanes automatically
# The speed limit of the road is 20m/s so the EGO should drive faster than the NPC
npc.follow_closest_lane(follow=True, max_speed=8, isLaneChange=False)

# t0 is the time when the Simulation started
t0 = time.time()

# This will keep track of if the NPC has already changed lanes
npcChangedLanes = False

# Run Simulation for 4 seconds before checking cut-in or end conditions
sim.run(4)

# The Simulation will pause every 0.5 seconds to check 2 conditions
while True:
    sim.run(0.5)

    # If the NPC has not already changed lanes then the distance between the NPC and EGO is calculated
    if not npcChangedLanes:
        egoCurrentState = ego.state
        npcCurrentState = npc.state

        separationDistance = (egoCurrentState.position - npcCurrentState.position).magnitude()

        # If the EGO and NPC are within 15m, then NPC will change lanes to the right (in front of the EGO)
        if separationDistance <= 15:
            npc.change_lane(False)
            npcChangedLanes = True

    # Simulation will be limited to running for 30 seconds total
    if time.time() - t0 > 26:
        break
