#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import math
from environs import Env
import lgsvl

print("Python API Quickstart #16: Pedestrian following waypoints")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

spawns = sim.get_spawn()
forward = lgsvl.utils.transform_to_forward(spawns[1])
right = lgsvl.utils.transform_to_right(spawns[1])

state = lgsvl.AgentState()
state.transform = spawns[1]
sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

# This will create waypoints in a circle for the pedestrian to follow
radius = 4
count = 8
wp = []
for i in range(count):
    x = radius * math.cos(i * 2 * math.pi / count)
    z = radius * math.sin(i * 2 * math.pi / count)
    # idle is how much time the pedestrian will wait once it reaches the waypoint
    idle = 1 if i < count // 2 else 0
    wp.append(
        lgsvl.WalkWaypoint(spawns[1].position + x * right + (z + 8) * forward, idle)
    )

state = lgsvl.AgentState()
state.transform = spawns[1]
state.transform.position = wp[0].position

p = sim.add_agent("Pamela", lgsvl.AgentType.PEDESTRIAN, state)


def on_waypoint(agent, index):
    print("Waypoint {} reached".format(index))


p.on_waypoint_reached(on_waypoint)

# This sends the list of waypoints to the pedestrian. The bool controls whether or not the pedestrian will continue walking (default false)
p.follow(wp, True)

input("Press Enter to walk in circle for 60 seconds")

sim.run(60)
