#!/usr/bin/env python3
#
# Copyright (c) 2019 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl
import time

sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)
if sim.current_scene == "BorregasAve":
  sim.reset()
else:
  sim.load("BorregasAve")

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
# Agents can be spawned with a velocity. Default is to spawn with 0 velocity
state.velocity = lgsvl.Vector(0, 0, 20)
a = sim.add_agent("Jaguar2015XE (Apollo 5.0)", lgsvl.AgentType.EGO, state)

# The bounding box of an agent are 2 points (min and max) such that the box formed from those 2 points completely encases the agent
print("Vehicle bounding box =", a.bounding_box)

print("Real time elapsed = ", 0)
print("Simulation time = ", sim.current_time)
print("Simulation frames = ", sim.current_frame)

input("Press Enter to drive forward for 100 frames")

# The simulator can be run for a set amount of time. time_limit is optional and if omitted or set to 0, then the simulator will run indefinitely
t0 = time.time()
sim.step(frames = 100, framerate = 20)
t1 = time.time()
print("Real time elapsed = ", t1 - t0)
print("Simulation time = ", sim.current_time)
print("Simulation frames = ", sim.current_frame)

input("Press Enter to continue driving for 100 frames")

t2 = time.time()
sim.step(frames = 100, framerate = 20)
t3 = time.time()

print("Real time elapsed = ", t3 - t2 + t1 - t0)
print("Simulation time = ", sim.current_time)
print("Simulation frames = ", sim.current_frame)
