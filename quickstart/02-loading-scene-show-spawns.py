#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl

print("Python API Quickstart #2: Loading the scene spawn points")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))

print("Current Scene = {}".format(sim.current_scene))

# Loads the named map in the connected simulator. The available maps can be set up in web interface
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

print("Current Scene = {}".format(sim.current_scene))
print("Current Scene ID = {}".format(sim.current_scene_id))

# This will print out the position and rotation vectors for each of the spawn points in the loaded map
spawns = sim.get_spawn()
for spawn in sim.get_spawn():
    print(spawn)
