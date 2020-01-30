#!/usr/bin/env python3
#
# Copyright (c) 2020 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl

sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)

scene_name = "CubeTown"

if sim.current_scene == scene_name:
  sim.reset()
else:
  sim.load(scene_name, 42)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])
up = lgsvl.utils.transform_to_up(spawns[0])
state.transform = spawns[0]

ego = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, state)

print("Python API Quickstart #28: How to Add/Control Traffic Cone")

for i in range(10*3):
  # Create controllables in a block
  start = spawns[0].position + (5 + (1.0 * (i//6))) * forward - (2 + (1.0 * (i % 6))) * right
  end = start + 10 * forward

  state = lgsvl.ObjectState()
  state.transform.position = start
  state.transform.rotation = spawns[0].rotation
  # Set velocity and angular_velocity
  state.velocity = 10 * up
  state.angular_velocity = 6.5 * right
  
  # add controllable
  o = sim.controllable_add("TrafficCone", state)
  

print("\nAdded {} Traffic Cones".format(i + 1))

seconds = 10
input("\nPress Enter to run simulation for {} seconds".format(seconds))
print("\nRunning simulation for {} seconds...".format(seconds))
sim.run(seconds)

print("\nDone!")
