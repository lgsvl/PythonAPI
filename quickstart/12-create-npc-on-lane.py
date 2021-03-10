#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import math
import random
from environs import Env
import lgsvl

print("Python API Quickstart #12: Creating NPCs on lanes")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

sx = spawns[0].position.x
sy = spawns[0].position.y
sz = spawns[0].position.z

mindist = 10.0
maxdist = 40.0

random.seed(0)

print("Spawn 10 random NPCs on lanes")
for i in range(10):
    input("Press Enter to spawn NPC ({})".format(i + 1))

    # Creates a random point around the EGO
    angle = random.uniform(0.0, 2 * math.pi)
    dist = random.uniform(mindist, maxdist)

    point = lgsvl.Vector(sx + dist * math.cos(angle), sy, sz + dist * math.sin(angle))

    # Creates an NPC on a lane that is closest to the random point
    state = lgsvl.AgentState()
    state.transform = sim.map_point_on_lane(point)
    sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)
