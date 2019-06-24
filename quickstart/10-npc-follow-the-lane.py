#!/usr/bin/env python3
#
# Copyright (c) 2019 LG Electronics, Inc.
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

state = lgsvl.AgentState()
state.transform = spawns[0]
a = sim.add_agent("Jaguar2015XE (Apollo 3.5)", lgsvl.AgentType.EGO, state)

state = lgsvl.AgentState()
state.transform = spawns[0]

sx = spawns[0].position.x
sz = spawns[0].position.z

# 10 meters ahead, on left lane
state.transform.position.z = sz + 10.0

npc1 = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)

state = lgsvl.AgentState()
state.transform = spawns[0]

# 10 meters ahead, on right lane
state.transform.position.x = sx + 4.0
state.transform.position.z = sz + 10.0

npc2 = sim.add_agent("SUV", lgsvl.AgentType.NPC, state)

# If the passed bool is False, then the NPC will not moved
# The float passed is the maximum speed the NPC will drive
# 11.1 m/s is ~40 km/h
npc1.follow_closest_lane(True, 11.1)

# 5.6 m/s is ~20 km/h
npc2.follow_closest_lane(True, 5.6)

input("Press Enter to run")

sim.run()
