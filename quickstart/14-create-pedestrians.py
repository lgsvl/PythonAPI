#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import random
import time
from environs import Env
import lgsvl

print("Python API Quickstart #14: Creating pedestrians on the map")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])
sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

input("Press Enter to create 100 pedestrians")

# The list of available pedestrians can be found in PedestrianManager prefab
names = [
    "Bob",
    "EntrepreneurFemale",
    "Howard",
    "Johny",
    "Pamela",
    "Presley",
    "Robin",
    "Stephen",
    "Zoe",
]

i = 0
while i < 100:
    state = lgsvl.AgentState()

    state.transform.position = (
        spawns[0].position
        + (5 + (1.0 * (i // 16))) * forward
        + (5 - (1.0 * (i % 16))) * right
    )
    state.transform.rotation = spawns[0].rotation
    name = random.choice(names)
    print("({}) adding {}".format(i + 1, name))
    p = sim.add_agent(name, lgsvl.AgentType.PEDESTRIAN, state)
    time.sleep(0.1)
    i += 1
