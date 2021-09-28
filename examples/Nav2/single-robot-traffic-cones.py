#!/usr/bin/env python3
#
# Copyright (c) 2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl

print("Navigation2 Example: Single Robot Traffic Cones")

TIME_DELAY = 5
TIME_LIMIT = 90
NAV_DST = ((10.9, -0, 0), (0, 0, 0, 1.0))

SIMULATOR_HOST = os.environ.get("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host)
SIMULATOR_PORT = int(os.environ.get("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
BRIDGE_HOST = os.environ.get("LGSVL__AUTOPILOT_0_HOST", lgsvl.wise.SimulatorSettings.bridge_host)
BRIDGE_PORT = int(os.environ.get("LGSVL__AUTOPILOT_0_PORT", lgsvl.wise.SimulatorSettings.bridge_port))

SCENE = os.environ.get("LGSVL__MAP", lgsvl.wise.DefaultAssets.map_lgseocho)
ROBOT = os.environ.get("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lgcloi_navigation2)

sim = lgsvl.Simulator(SIMULATOR_HOST, SIMULATOR_PORT)
if sim.current_scene == SCENE:
    sim.reset()
else:
    sim.load(SCENE, seed=0)

spawns = sim.get_spawn()
state = lgsvl.AgentState()
state.transform = spawns[0]

ego = sim.add_agent(ROBOT, lgsvl.AgentType.EGO, state)
ego.connect_bridge(BRIDGE_HOST, BRIDGE_PORT)
ego.set_initial_pose()
sim.run(TIME_DELAY)
is_reached = False


def on_destination_reached(agent):
    global is_reached
    is_reached = True
    print(f"Robot reached destination")
    sim.stop()
    return


sim_dst = sim.map_from_nav(lgsvl.Vector(*NAV_DST[0]), lgsvl.Quaternion(*NAV_DST[1]))
ego.set_destination(sim_dst)
res = ego.on_destination_reached(on_destination_reached)

right = lgsvl.utils.transform_to_right(state.transform)
forward = lgsvl.utils.transform_to_forward(state.transform)

sign = 1
for j in range(2, 11, 2):
    sign *= -1
    for i in range(5):
        objState = lgsvl.ObjectState()
        objState.transform.position = state.transform.position
        offset = sign * 0.5 * i * right + j * forward
        objState.transform.position += offset
        sim.controllable_add("TrafficCone", objState)


def on_collision(agent1, agent2, contact):
    name1 = "traffic cone" if agent1 is None else agent1.name
    name2 = "traffic cone" if agent2 is None else agent2.name
    raise Exception("Failed: {} collided with {}".format(name1, name2))


ego.on_collision(on_collision)
print(f"Running simulation for {TIME_LIMIT} seconds...")
sim.run(TIME_LIMIT)

if is_reached:
    print("PASSED")
else:
    exit("FAILED: Ego did not reach the destination")
