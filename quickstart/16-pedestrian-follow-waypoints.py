#!/usr/bin/env python3
#
# Copyright (c) 2019-2020 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import math
from environs import Env
import lgsvl

env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))
if sim.current_scene == "BorregasAve":
    sim.reset()
else:
    sim.load("BorregasAve")

spawns = sim.get_spawn()
forward = lgsvl.utils.transform_to_forward(spawns[1])
right = lgsvl.utils.transform_to_right(spawns[1])

state = lgsvl.AgentState()
state.transform = spawns[1]
sim.add_agent(env.str("LGSVL__VEHICLE_0", "Lincoln2017MKZ (Apollo 5.0)"), lgsvl.AgentType.EGO, state)

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

input("Press Enter to walk in circle")

sim.run()
