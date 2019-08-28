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
a = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, state)

print("Current time:", sim.time_of_day)

input("Press Enter to set fixed time to 19:00")

# Time of day can be set from 0 ... 24
sim.set_time_of_day(19.0)
print(sim.time_of_day)

sim.run(5)

input("Press Enter to set normal time to 10:30")
# Normal time moves forward (at an accelerated rate). Pass False to set_time_of_day for this to happen
sim.set_time_of_day(10.5, False)
print(sim.time_of_day)

sim.run(5)

print(sim.time_of_day)
