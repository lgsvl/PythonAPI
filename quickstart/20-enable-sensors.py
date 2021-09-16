#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl

print("Python API Quickstart #20: Enabling and disabling sensors")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[1]
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

sensors = ego.get_sensors()

# Sensors have an enabled/disabled state that can be set
# By default all sensors are enabled
# Disabling sensor will prevent it to send or receive messages to ROS or Cyber bridges
lidarAvailable = False
for s in sensors:
    print(type(s), s.enabled)
    if isinstance(s, lgsvl.LidarSensor):
        lidarAvailable = True

if lidarAvailable:
    input("Press Enter to disable LiDAR")

    for s in sensors:
        if isinstance(s, lgsvl.LidarSensor):
            s.enabled = False

    for s in sensors:
        print(type(s), s.enabled)
else:
    print("LiDAR sensor is not included in the selected sensor configuration. Please check the \"ego_lincoln2017mkz_apollo5\" sensor configuration in the default assets.")
    input("Press Enter to stop the simulation")
