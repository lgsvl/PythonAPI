#!/usr/bin/env python3
#
# Copyright (c) 2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import lgsvl
from environs import Env
from lgsvl import Vector, Quaternion

print("Python API Quickstart #36: Sending destinations to Navigation2")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))

map_seocho = lgsvl.wise.DefaultAssets.map_lgseocho
ego_cloi = lgsvl.wise.DefaultAssets.ego_lgcloi_navigation2

if sim.current_scene == map_seocho:
    sim.reset()
else:
    sim.load(map_seocho)

sim.set_time_of_day(0, fixed=True)
spawns = sim.get_spawn()
state = lgsvl.AgentState()
state.transform = spawns[0]

ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", ego_cloi), lgsvl.AgentType.EGO, state)
ego.connect_bridge(env.str("LGSVL__AUTOPILOT_0_HOST", lgsvl.wise.SimulatorSettings.bridge_host), env.int("LGSVL__AUTOPILOT_0_PORT", lgsvl.wise.SimulatorSettings.bridge_port))

i = 0

# List of destinations in Nav2 costmap coordinates
ros_destinations = [
    ((3.118, -0.016, 0), (0, 0, 0.0004, 0.999)),
    ((3.126, -10.025, 0), (0, 0, 0.006, 0.999)),
    ((11.171, -9.875, 0), (0, 0, 0.707, 0.707)),
    ((11.882, -0.057, 0), (0, 0, 0.699, 0.715)),
    ((12.351, 11.820, 0), (0, 0, -0.999, 0.0004)),
    ((2.965, 11.190, 0), (0, 0, -0.707, 0.707)),
    ((2.687, -0.399, 0), (0, 0, -0.0036, 0.999)),
]

ego.set_initial_pose()
sim.run(5)


def send_next_destination(agent):
    global i
    print(f"{i}: {agent.name} reached destination")
    i += 1
    if i >= len(ros_destinations):
        print("Iterated all destinations successfully. Stopping...")
        sim.stop()
        return

    ros_dst = ros_destinations[i]
    next_dst = sim.map_from_nav(Vector(*ros_dst[0]), Quaternion(*ros_dst[1]))
    ego.set_destination(next_dst)


ros_dst = ros_destinations[0]
first_dst = sim.map_from_nav(Vector(*ros_dst[0]), Quaternion(*ros_dst[1]))
ego.set_destination(first_dst)
ego.on_destination_reached(send_next_destination)

sim.run()

print("Done!")
