#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl
from datetime import datetime

print("Python API Quickstart #19: Changing the time of day")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

print("Current time:", sim.time_of_day)

input("Press Enter to set fixed time to 19:00")

# Time of day can be set from 0 ... 24
sim.set_time_of_day(19.0)
print(sim.time_of_day)

sim.run(5)

input("Press Enter to set normal time to 10:30")
# Normal time moves forward (at an accelerated rate). Pass False to set_time_of_day for this to happen
sim.set_time_of_day(10.5, False)
print(sim.time_of_day)

sim.run(5)

print(sim.time_of_day)

input("Press Enter to set date to July 1 2020 and time to 19:00")
dt = datetime(2020, 7, 1, 19, 0, 0, 0)
sim.set_date_time(dt, False)
print(sim.time_of_day)
print(sim.current_datetime)

sim.run(5)

print(sim.time_of_day)
print(sim.current_datetime)
