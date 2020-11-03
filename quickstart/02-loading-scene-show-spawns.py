#!/usr/bin/env python3
#
# Copyright (c) 2019-2020 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl

env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))

print("Current Scene = {}".format(sim.current_scene))

# Loads the named map in the connected simulator. The available maps can be set up in web interface
if sim.current_scene == "BorregasAve":
    sim.reset()
else:
    sim.load("BorregasAve")

print("Current Scene = {}".format(sim.current_scene))
print("Current Scene ID = {}".format(sim.current_scene_id))

# This will print out the position and rotation vectors for each of the spawn points in the loaded map
spawns = sim.get_spawn()
for spawn in sim.get_spawn():
    print(spawn)
