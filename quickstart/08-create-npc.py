#!/usr/bin/env python3
#
# Copyright (c) 2019 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl
import random

sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)
if sim.current_scene == "BorregasAve":
  sim.reset()
else:
  sim.load("BorregasAve")

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
a = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, state)

# Spawn NPC vehicles 10 meters ahead of the EGO
sx = spawns[0].position.x
sz = spawns[0].position.z + 10.0

# Spawns one of each of the listed types of NPCS
# The first will be created in front of the EGO and then they will be created to the left
# The available types of NPCs can be found in NPCManager prefab
for i, name in enumerate(["Sedan", "SUV", "Jeep", "Hatchback"]):
  state = lgsvl.AgentState()
  state.transform = spawns[0]

  state.transform.position.x = sx - 4.0 * i
  state.transform.position.z = sz
  sim.add_agent(name, lgsvl.AgentType.NPC, state)
