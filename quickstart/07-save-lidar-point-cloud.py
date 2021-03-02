#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl
from settings import *

print("Python API Quickstart #7: Saving a point cloud from the Lidar sensor")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", SimulatorSettings.simulatorHost), env.int("LGSVL__SIMULATOR_PORT", SimulatorSettings.simulatorPort))
if sim.current_scene == SimulatorSettings.map_borregasave:
    sim.reset()
else:
    sim.load(SimulatorSettings.map_borregasave)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", SimulatorSettings.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

sensors = ego.get_sensors()
for s in sensors:
    if s.name == "Lidar":
        s.save("lidar.pcd")
        break
