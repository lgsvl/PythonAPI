#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl
from settings import *

print("Python API Quickstart #18: Changing the weather effects")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", SimulatorSettings.simulatorHost), env.int("LGSVL__SIMULATOR_PORT", SimulatorSettings.simulatorPort))
if sim.current_scene == SimulatorSettings.map_borregasave:
    sim.reset()
else:
    sim.load(SimulatorSettings.map_borregasave)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
sim.add_agent(env.str("LGSVL__VEHICLE_0", SimulatorSettings.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

print(sim.weather)

input("Press Enter to set rain to 80%")

# Each weather variable is a float from 0 to 1
# There is no default value so each varible must be specified
sim.weather = lgsvl.WeatherState(rain=0.8, fog=0, wetness=0, cloudiness=0, damage=0)
print(sim.weather)

sim.run(5)

input("Press Enter to set fog to 50%")

sim.weather = lgsvl.WeatherState(rain=0, fog=0.5, wetness=0, cloudiness=0, damage=0)
print(sim.weather)

sim.run(5)

input("Press Enter to set wetness to 50%")

sim.weather = lgsvl.WeatherState(rain=0, fog=0, wetness=0.5, cloudiness=0, damage=0)
print(sim.weather)

sim.run(5)

input("Press Enter to reset to 0")

sim.weather = lgsvl.WeatherState(rain=0, fog=0, wetness=0, cloudiness=0, damage=0)
print(sim.weather)

sim.run(5)
