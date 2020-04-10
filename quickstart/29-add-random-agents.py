#!/usr/bin/env python3
#
# Copyright (c) 2020 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl

sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)
if sim.current_scene == "BorregasAve":
  sim.reset()
else:
  sim.load("BorregasAve")

spawns = sim.get_spawn()
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])

sx = spawns[0].position.x
sz = spawns[0].position.z

state = lgsvl.AgentState()
state.transform.position = spawns[0].position + 40 * forward
state.transform.rotation = spawns[0].rotation

a = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, state)

sim.add_random_agents(lgsvl.AgentType.NPC)
sim.add_random_agents(lgsvl.AgentType.PEDESTRIAN)

input("Press Enter to start")

sim.run()
