#!/usr/bin/env python3
#
# Copyright (c) 2019 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl

sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)

scene_name = "BorregasAve"

if sim.current_scene == scene_name:
  sim.reset()
else:
  sim.load(scene_name, 42)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
state.velocity = lgsvl.Vector(0, 0, 20)
ego = sim.add_agent("Jaguar2015XE (Apollo 5.0)", lgsvl.AgentType.EGO, state)

print("Python API Quickstart #27: How to Control Traffic Light")

# Get a list of controllable objects
controllables = sim.get_controllables()
print("\n# List of controllable objects in {} scene:".format(scene_name))
for c in controllables:
  print(c)

# Pick a traffic light of intrest
signal = controllables[2]

# Get current controllable states
print("\n# Current control policy:")
print(signal.control_policy)

# Create a new control policy
control_policy = "trigger=50;green=1;yellow=1.5;red=2;green=5;loop"

# Control this traffic light with a new control policy
signal.control(control_policy)

print("\n# Updated control policy:")
print(signal.control_policy)

# Get current state of signal
print("\n# Current signal state before simulation:")
print(signal.current_state)

seconds = 10
input("\nPress Enter to run simulation for {} seconds".format(seconds))
print("\nRunning simulation for {} seconds...".format(seconds))
sim.run(seconds)

print("\n# Current signal state after simulation:")
print(signal.current_state)
print("\nDone!")
