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

state = lgsvl.AgentState()
state.transform = spawns[0]
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])
a = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, state)

sx = state.transform.position.x
sz = state.transform.position.z

input("Press Enter to start creating pedestrians")

# The list of available pedestrians can be found in PedestrianManager prefab
names = ["Bob", "EntrepreneurFemale", "Howard", "Johny", "Pamela", "Presley", "Robin", "Stephen", "Zoe"]

i = 0
while True:
  state = lgsvl.AgentState()

  state.transform.position = spawns[0].position + (5 + (1.0 * (i//16))) * forward + (5 - (1.0 * (i % 16))) * right
  state.transform.rotation = spawns[0].rotation
  name = random.choice(names)
  print("({}) adding {}".format(i+1, name))
  p = sim.add_agent(name, lgsvl.AgentType.PEDESTRIAN, state)
  time.sleep(0.1)
  i += 1
