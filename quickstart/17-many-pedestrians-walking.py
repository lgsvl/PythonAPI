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
sy = state.transform.position.y
sz = state.transform.position.z

names = ["Bob", "EntrepreneurFemale", "Howard", "Johny", "Pamela", "Presley", "Robin", "Stephen", "Zoe"]

for i in range(20*6):
  # Create peds in a block
  start = spawns[0].position + (5 + (1.0 * (i//6))) * forward - (2 + (1.0 * (i % 6))) * right
  end = start + 10 * forward

# Give waypoints for the spawn location and 10m ahead
  wp = [ lgsvl.WalkWaypoint(start, 0),
         lgsvl.WalkWaypoint(end, 0),
       ]

  state = lgsvl.AgentState()
  state.transform.position = start
  state.transform.rotation = spawns[0].rotation
  name = random.choice(names)

# Send the waypoints and make the pedestrian loop over the waypoints
  p = sim.add_agent(name, lgsvl.AgentType.PEDESTRIAN, state)
  p.follow(wp, True)

input("Press Enter to start")

sim.run()
