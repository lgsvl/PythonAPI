#!/usr/bin/env python3
#
# Copyright (c) 2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl

env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))
if sim.current_scene == "BorregasAve":
    sim.reset()
else:
    sim.load("BorregasAve")

# This creates a transform in Unity world coordinates
tr = lgsvl.Transform(lgsvl.Vector(10, 50, 0), lgsvl.Vector(90, 0, 0))

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
forward = lgsvl.utils.transform_to_forward(spawns[0])
state.velocity = 20 * forward
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", "Lincoln2017MKZ (Apollo 5.0)"), lgsvl.AgentType.EGO, state)

# This function sets the camera to free state and applies the transform to the camera rig
sim.set_sim_camera(tr)
print("Set transform: {}".format(tr))

input("Press Enter to drive forward for 4 seconds")
sim.run(time_limit=4.0)
