#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl
from settings import *

print("Python API Quickstart #20: Enabling and disabling sensors")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", SimulatorSettings.simulatorHost), env.int("LGSVL__SIMULATOR_PORT", SimulatorSettings.simulatorPort))
if sim.current_scene == SimulatorSettings.mapName:
    sim.reset()
else:
    sim.load(SimulatorSettings.mapName)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[1]
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", SimulatorSettings.egoVehicleWithLidar), lgsvl.AgentType.EGO, state)

sensors = ego.get_sensors()

# Sensors have an enabled/disabled state that can be set
# By default all sensors are enabled
# Disabling sensor will prevent it to send or receive messages to ROS or Cyber bridges
for s in sensors:
    print(type(s), s.enabled)

input("Press Enter to disable lidar")

for s in sensors:
    if isinstance(s, lgsvl.LidarSensor):
        s.enabled = False

for s in sensors:
    print(type(s), s.enabled)
