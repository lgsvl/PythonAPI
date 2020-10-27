#!/usr/bin/env python3
#
# Copyright (c) 2019-2020 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import math
import random
from environs import Env
import lgsvl

env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))
if sim.current_scene == "BorregasAve":
    sim.reset()
else:
    sim.load("BorregasAve")

spawns = sim.get_spawn()
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])

state = lgsvl.AgentState()
state.transform = sim.map_point_on_lane(spawns[0].position + 200 * forward)
sim.add_agent(env.str("LGSVL__VEHICLE_0", "Lincoln2017MKZ (Apollo 5.0)"), lgsvl.AgentType.EGO, state)

mindist = 10.0
maxdist = 40.0

random.seed(0)


# Along with collisions and waypoints, NPCs can send a callback when they change lanes and reach a stopline
def on_stop_line(agent):
    print(agent.name, "reached stop line")


# This will be called when an NPC begins to change lanes
def on_lane_change(agent):
    print(agent.name, "is changing lanes")


# This creates 4 NPCs randomly in an area around the EGO
for name in ["Sedan", "SUV", "Jeep", "Hatchback"]:
    angle = random.uniform(0.0, 2 * math.pi)
    dist = random.uniform(mindist, maxdist)

    point = (
        spawns[0].position
        + dist * math.sin(angle) * right
        + (225 + dist * math.cos(angle)) * forward
    )

    state = lgsvl.AgentState()
    state.transform = sim.map_point_on_lane(point)
    npc = sim.add_agent(name, lgsvl.AgentType.NPC, state)
    npc.follow_closest_lane(True, 10)
    npc.on_lane_change(on_lane_change)
    npc.on_stop_line(on_stop_line)

sim.run()
