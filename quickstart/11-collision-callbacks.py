#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl

print("Python API Quickstart #11: Handling the collision callbacks")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

spawns = sim.get_spawn()
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])

# ego vehicle
state = lgsvl.AgentState()
state.transform = spawns[0]
state.velocity = 6 * forward
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

# school bus, 20m ahead, perpendicular to road, stopped
state = lgsvl.AgentState()
state.transform.position = spawns[0].position + 20.0 * forward
state.transform.rotation.y = spawns[0].rotation.y + 90.0
bus = sim.add_agent("SchoolBus", lgsvl.AgentType.NPC, state)

# sedan, 10m ahead, driving forward
state = lgsvl.AgentState()
state.transform.position = spawns[0].position + 10.0 * forward
state.transform.rotation = spawns[0].rotation
sedan = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)
# Even though the sedan is commanded to follow the lane, obstacle avoidance takes precedence and it will not drive into the bus
sedan.follow_closest_lane(True, 11.1)  # 11.1 m/s is ~40 km/h

vehicles = {
    ego: "EGO",
    bus: "SchoolBus",
    sedan: "Sedan",
}


# This function gets called whenever any of the 3 vehicles above collides with anything
def on_collision(agent1, agent2, contact):
    name1 = vehicles[agent1]
    name2 = vehicles[agent2] if agent2 is not None else "OBSTACLE"
    print("{} collided with {} at {}".format(name1, name2, contact))


# The above on_collision function needs to be added to the callback list of each vehicle
ego.on_collision(on_collision)
bus.on_collision(on_collision)
sedan.on_collision(on_collision)

input("Press Enter to run the simulation for 10 seconds")

# Drive into the sedan, bus, or obstacle to get a callback
sim.run(10)
