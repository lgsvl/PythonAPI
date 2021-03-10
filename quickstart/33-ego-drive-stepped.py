#!/usr/bin/env python3
#
# Copyright (c) 2020-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl
import time

print("Python API Quickstart #33: Stepping a simulation")
sim = lgsvl.Simulator(os.environ.get("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), lgsvl.wise.SimulatorSettings.simulator_port)
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
# Re-load scene and set random seed
sim.load(lgsvl.wise.DefaultAssets.map_borregasave, seed=123)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
forward = lgsvl.utils.transform_to_forward(spawns[0])

# Agents can be spawned with a velocity. Default is to spawn with 0 velocity
# state.velocity = 20 * forward

# In order for Apollo to drive with stepped simulation we must add the clock sensor
# and we must also set clock_mode to MODE_MOCK in Apollo's cyber/conf/cyber.pb.conf
# Note that MODE_MOCK is only supported in Apollo master (6.0 or later)!
# Refer to https://www.svlsimulator.com/docs/sensor-json-options/#clock

# We can test Apollo with standard MKZ or MKZ with ground truth sensors
# Refer to https://www.svlsimulator.com/docs/modular-testing/
ego = sim.add_agent(lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5, lgsvl.AgentType.EGO, state)

# An EGO will not connect to a bridge unless commanded to
print("Bridge connected:", ego.bridge_connected)

# The EGO looks for a (Cyber) bridge at the specified IP and port
ego.connect_bridge(lgsvl.wise.SimulatorSettings.bridge_host, lgsvl.wise.SimulatorSettings.bridge_port)
# uncomment to wait for bridge connection; script will drive ego if bridge not found
# print("Waiting for connection...")
# while not ego.bridge_connected:
time.sleep(1)

print("Bridge connected:", ego.bridge_connected)

# spawn random NPCs
sim.add_random_agents(lgsvl.AgentType.NPC)
sim.add_random_agents(lgsvl.AgentType.PEDESTRIAN)

t0 = time.time()
s0 = sim.current_time
print()
print("Total real time elapsed = {:5.3f}".format(0))
print("Simulation time = {:5.1f}".format(s0))
print("Simulation frames =", sim.current_frame)

# let simulator initialize and settle a bit before starting
sim.run(time_limit=2)

t1 = time.time()
s1 = sim.current_time
print()
print("Total real time elapsed = {:5.3f}".format(t1 - t0))
print("Simulation settle time = {:5.1f}".format(s1 - s0))
print("Simulation settle frames =", sim.current_frame)

# tell ego to drive forward, or not (if apollo is driving)
if not ego.bridge_connected:
    state = ego.state
    forward = lgsvl.utils.transform_to_forward(state.transform)
    state.velocity = 20 * forward
    ego.state = state
    duration = 15
else:
    duration = 45

step_time = 0.10

step_rate = int(1.0 / step_time)
steps = duration * step_rate
print()
print("Stepping forward for {} steps of {}s per step" .format(steps, step_time))
input("Press Enter to start:")

# The simulator can be run for a set amount of time.
# time_limit is optional and if omitted or set to 0, then the simulator will run indefinitely
t0 = time.time()
for i in range(steps):
    t1 = time.time()
    sim.run(time_limit=step_time)
    t2 = time.time()
    s2 = sim.current_time

    state = ego.state
    pos = state.position
    speed = state.speed * 3.6

    # if Apollo is not driving
    if not ego.bridge_connected:
        state.velocity = 20 * forward
        ego.state = state

    print("Sim time = {:5.2f}".format(s2 - s1) + "; Real time elapsed = {:5.3f}; ".format(t2 - t1), end='')
    print("Speed = {:4.1f}; Position = {:5.3f},{:5.3f},{:5.3f}".format(speed, pos.x, pos.y, pos.z))
    time.sleep(0.2)

t3 = time.time()

# Final statistics
print("Total real time elapsed = {:5.3f}".format(t3 - t0))
print("Simulation time = {:5.1f}".format(sim.current_time))
print("Simulation frames =", sim.current_frame)
