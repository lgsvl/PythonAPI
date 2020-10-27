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
if sim.current_scene == "BorregasAve":
    sim.reset()
else:
    sim.load("BorregasAve")

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
sim.add_agent(env.str("LGSVL__VEHICLE_0", "Lincoln2017MKZ (Apollo 5.0)"), lgsvl.AgentType.EGO, state)

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
