#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import time
from environs import Env
import lgsvl

print("Python API Quickstart #24: Changing the Simulator timescale")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
forward = lgsvl.utils.transform_to_forward(spawns[0])
# Agents can be spawned with a velocity. Default is to spawn with 0 velocity
state.velocity = 20 * forward
sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

print("Real time elapsed =", 0)
print("Simulation time =", sim.current_time)
print("Simulation frames =", sim.current_frame)

input("Press Enter to drive forward for 4 seconds (2x)")

# The simulator can be run for a set amount of time. time_limit is optional and if omitted or set to 0, then the simulator will run indefinitely
t0 = time.time()
sim.run(time_limit=4, time_scale=2)
t1 = time.time()
print("Real time elapsed =", t1 - t0)
print("Simulation time =", sim.current_time)
print("Simulation frames =", sim.current_frame)

current_sim_time = sim.current_time
current_sim_frames = sim.current_frame

input("Press Enter to continue driving for 2 more seconds (0.5x)")

t2 = time.time()
sim.run(time_limit=2, time_scale=0.5)
t3 = time.time()

print("Real time elapsed =", t3 - t2)
print("Simulation time =", sim.current_time - current_sim_time)
print("Simulation frames =", sim.current_frame - current_sim_frames)
