#!/usr/bin/env python3
#
# Copyright (c) 2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl

print("Navigation2 Example: Single Robot Cut In")

TIME_DELAY = 5
TIME_LIMIT = 70
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
egoState = lgsvl.AgentState()
egoState.transform = spawns[0]

ego = sim.add_agent(ROBOT, lgsvl.AgentType.EGO, egoState)
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

right = lgsvl.utils.transform_to_right(egoState.transform)
forward = lgsvl.utils.transform_to_forward(egoState.transform)

pedState = lgsvl.AgentState()
pedState.transform.position = egoState.transform.position
pedState.transform.position += 5 * right + 5 * forward
ped = sim.add_agent("Robin", lgsvl.AgentType.PEDESTRIAN, pedState)


def on_collision(agent1, agent2, contact):
    raise Exception("Failed: {} collided with {}".format(agent1, agent2))


ego.on_collision(on_collision)
ped.on_collision(on_collision)
waypoints = []
waypoints.append(lgsvl.WalkWaypoint(pedState.position, idle=0, trigger_distance=6))
waypoints.append(lgsvl.WalkWaypoint(pedState.transform.position - 5 * right, idle=15))
waypoints.append(lgsvl.WalkWaypoint(pedState.transform.position - 10 * right, idle=0))
ped.follow(waypoints)

print(f"Running simulation for {TIME_LIMIT} seconds...")
sim.run(TIME_LIMIT)

if is_reached:
    print("PASSED")
else:
    exit("FAILED: Ego did not reach the destination")
