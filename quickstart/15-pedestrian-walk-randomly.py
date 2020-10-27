#!/usr/bin/env python3
#
# Copyright (c) 2019-2020 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

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
state.transform.position = spawns[0].position + 40 * forward
state.transform.rotation = spawns[0].rotation

sim.add_agent(env.str("LGSVL__VEHICLE_0", "Lincoln2017MKZ (Apollo 5.0)"), lgsvl.AgentType.EGO, state)

state = lgsvl.AgentState()
# Spawn the pedestrian in front of car
state.transform.position = spawns[0].position + 50 * forward
state.transform.rotation = spawns[0].rotation

p = sim.add_agent("Bob", lgsvl.AgentType.PEDESTRIAN, state)
# Pedestrian will walk to a random point on sidewalk
p.walk_randomly(True)

input("Press Enter to walk")

sim.run(10)

input("Press Enter to stop")
# With walk_randomly passed False, pedestrian will stop walking
p.walk_randomly(False)

sim.run(5)
