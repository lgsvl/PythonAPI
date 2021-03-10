#!/usr/bin/env python3
#
# Copyright (c) 2019 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from datetime import datetime
import random
from environs import Env

import lgsvl


'''
LGSVL__AUTOPILOT_0_HOST             IP address of the computer running the bridge to connect to
LGSVL__AUTOPILOT_0_PORT             Port that the bridge listens on for messages
LGSVL__AUTOPILOT_0_VEHICLE_CONFIG   Vehicle configuration to be loaded in Dreamview (Capitalization and spacing must match the dropdown in Dreamview)
LGSVL__AUTOPILOT_HD_MAP             HD map to be loaded in Dreamview (Capitalization and spacing must match the dropdown in Dreamview)
LGSVL__AUTOPILOT_0_VEHICLE_MODULES  List of modules to be enabled in Dreamview (Capitalization and space must match the sliders in Dreamview)
LGSVL__DATE_TIME                    Date and time to start simulation at, format 'YYYY-mm-ddTHH:MM:SS'
LGSVL__ENVIRONMENT_CLOUDINESS       Value of clouds weather effect, clamped to [0, 1]
LGSVL__ENVIRONMENT_DAMAGE           Value of road damage effect, clamped to [0, 1]
LGSVL__ENVIRONMENT_FOG              Value of fog weather effect, clamped to [0, 1]
LGSVL__ENVIRONMENT_RAIN             Value of rain weather effect, clamped to [0, 1]
LGSVL__ENVIRONMENT_WETNESS          Value of wetness weather effect, clamped to [0, 1]
LGSVL__MAP                          Name of map to be loaded in Simulator
LGSVL__RANDOM_SEED                  Seed used to determine random factors (e.g. NPC type, color, behaviour)
LGSVL__SIMULATION_DURATION_SECS     How long to run the simulation for
LGSVL__SIMULATOR_HOST               IP address of computer running simulator (Master node if a cluster)
LGSVL__SIMULATOR_PORT               Port that the simulator allows websocket connections over
LGSVL__SPAWN_BICYCLES               Wether or not to spawn bicycles
LGSVL__SPAWN_PEDESTRIANS            Whether or not to spawn pedestrians
LGSVL__SPAWN_TRAFFIC                Whether or not to spawn NPC vehicles
LGSVL__TIME_OF_DAY                  If LGSVL__DATE_TIME is not set, today's date is used and this sets the time of day to start simulation at, clamped to [0, 24]
LGSVL__TIME_STATIC                  Whether or not time should remain static (True = time is static, False = time moves forward)
LGSVL__VEHICLE_0                    Name of EGO vehicle to be loaded in Simulator
'''

env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))
scene_name = env.str("LGSVL__MAP", lgsvl.wise.DefaultAssets.map_borregasave)
try:
    sim.load(scene_name, env.int("LGSVL__RANDOM_SEED"))
except Exception:
    if sim.current_scene == scene_name:
        sim.reset()
    else:
        sim.load(scene_name)


def clamp(val, min_v, max_v):
    return min(max(val, min_v), max_v)


try:
    date_time = env.str("LGSVL__DATE_TIME")
except Exception:
    date_time = "1970-01-01T00:00:00"
else:
    static_time = env.bool("LGSVL__TIME_STATIC", True)
    if date_time == "1970-01-01T00:00:00":
        time_of_day = clamp(env.float("LGSVL__TIME_OF_DAY", 12), 0, 24)
        sim.set_time_of_day(time_of_day, static_time)
    else:
        sim.set_date_time(datetime.strptime(date_time[:19], '%Y-%m-%dT%H:%M:%S'), static_time)


rain = clamp(env.float("LGSVL__ENVIRONMENT_RAIN", 0), 0, 1)
fog = clamp(env.float("LGSVL__ENVIRONMENT_FOG", 0), 0, 1)
wetness = clamp(env.float("LGSVL__ENVIRONMENT_WETNESS", 0), 0, 1)
cloudiness = clamp(env.float("LGSVL__ENVIRONMENT_CLOUDINESS", 0), 0, 1)
damage = clamp(env.float("LGSVL__ENVIRONMENT_DAMAGE", 0), 0, 1)

sim.weather = lgsvl.WeatherState(rain, fog, wetness, cloudiness, damage)

spawns = sim.get_spawn()
spawn_index = random.randrange(len(spawns))

state = lgsvl.AgentState()
state.transform = spawns[spawn_index]  # TODO some sort of Env Variable so that user/wise can select from list
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5_full_analysis), lgsvl.AgentType.EGO, state)

# The EGO is now looking for a bridge at the specified IP and port
BRIDGE_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
ego.connect_bridge(BRIDGE_HOST, env.int("LGSVL__AUTOPILOT_0_PORT", 9090))

dv = lgsvl.dreamview.Connection(sim, ego, BRIDGE_HOST)
dv.set_hd_map(env.str("LGSVL__AUTOPILOT_HD_MAP", "Borregas Ave"))
dv.set_vehicle(env.str("LGSVL__AUTOPILOT_0_VEHICLE_CONFIG", 'Lincoln2017MKZ'))
default_modules = [
    'Localization',
    'Perception',
    'Transform',
    'Routing',
    'Prediction',
    'Planning',
    'Traffic Light',
    'Control',
    'Recorder'
]

try:
    modules = env.list("LGSVL__AUTOPILOT_0_VEHICLE_MODULES", subcast=str)
    if len(modules) == 0:
        modules = default_modules
except Exception:
    modules = default_modules

destination_index = random.randrange(len(spawns[spawn_index].destinations))
destination = spawns[spawn_index].destinations[destination_index] # TODO some sort of Env Variable so that user/wise can select from list
dv.setup_apollo(destination.position.x, destination.position.z, modules)

if env.bool("LGSVL__SPAWN_TRAFFIC", True):
    sim.add_random_agents(lgsvl.AgentType.NPC)

if env.bool("LGSVL__SPAWN_PEDESTRIANS", True):
    sim.add_random_agents(lgsvl.AgentType.PEDESTRIAN)

sim.run(env.float("LGSVL__SIMULATION_DURATION_SECS", 0))
