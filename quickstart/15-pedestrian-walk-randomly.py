#!/usr/bin/env python3
#
# Copyright (c) 2019 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl
import random
import time

sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)
if sim.current_scene == "BorregasAve":
  sim.reset()
else:
  sim.load("BorregasAve")

spawns = sim.get_spawn()
sx = spawns[0].position.x
sz = spawns[0].position.z

state = lgsvl.AgentState()
state.transform = spawns[0]
state.transform.position.z += 40

a = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, state)

state = lgsvl.AgentState()
state.transform = spawns[0]
# Spawn the pedestrian in front of car
state.transform.position.z = sz + 50

p = sim.add_agent("Bob", lgsvl.AgentType.PEDESTRIAN, state)
# Pedestrian will walk to a random point on sidewalk
p.walk_randomly(True)

input("Press Enter to walk")

sim.run(10)

input("Press Enter to stop")
# With walk_randomly passed False, pedestrian will stop walking
p.walk_randomly(False)

sim.run(5)
