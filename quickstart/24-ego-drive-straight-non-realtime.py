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
forward = lgsvl.utils.transform_to_forward(spawns[0])
# Agents can be spawned with a velocity. Default is to spawn with 0 velocity
state.velocity = 20 * forward
a = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, state)

print("Real time elapsed =", 0)
print("Simulation time =", sim.current_time)
print("Simulation frames =", sim.current_frame)

input("Press Enter to drive forward for 4 seconds (2x)")

# The simulator can be run for a set amount of time. time_limit is optional and if omitted or set to 0, then the simulator will run indefinitely
t0 = time.time()
sim.run(time_limit = 4, time_scale = 2)
t1 = time.time()
print("Real time elapsed =", t1 - t0)
print("Simulation time =", sim.current_time)
print("Simulation frames =", sim.current_frame)

current_sim_time = sim.current_time
current_sim_frames = sim.current_frame

input("Press Enter to continue driving for 2 more seconds (0.5x)")

t2 = time.time()
sim.run(time_limit = 2, time_scale = 0.5)
t3 = time.time()

print("Real time elapsed =", t3 - t2)
print("Simulation time =", sim.current_time - current_sim_time)
print("Simulation frames =", sim.current_frame - current_sim_frames)
