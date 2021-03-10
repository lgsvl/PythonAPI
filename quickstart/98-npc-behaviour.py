#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import math
import random
from environs import Env
import lgsvl

print("Python API Quickstart #98: Simulating different NPCs behaviours")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))

drunkDriverAvailable = False
trailerAvailable = 0

print("Current Scene = {}".format(sim.current_scene))
# Loads the named map in the connected simulator.
if sim.current_scene == lgsvl.wise.DefaultAssets.map_cubetown:
    sim.reset()
else:
    print("Loading Scene = {}".format(lgsvl.wise.DefaultAssets.map_cubetown))
    sim.load(lgsvl.wise.DefaultAssets.map_cubetown)

agents = sim.available_agents
print("agents:")
for i in range(len(agents)):
    agent = agents[i]
    if agent["name"] == "TrailerTruckTest":
        trailerAvailable |= 1
    if agent["name"] == "MackAnthemStandupSleeperCab2018":
        trailerAvailable |= 2
    print(
        "#{:>2}: {} {:40} ({:9}) {}".format(
            i,
            ("✔️" if agent["loaded"] else "❌"),
            agent["name"],
            agent["NPCType"],
            agent["AssetGuid"],
        )
    )

behaviours = sim.available_npc_behaviours


print("behaviours:")
for i in range(len(behaviours)):
    if behaviours[i]["name"] == "NPCDrunkDriverBehaviour":
        drunkDriverAvailable = True
    if behaviours[i]["name"] == "NPCTrailerBehaviour":
        trailerAvailable |= 4
    print("#{:>2}: {}".format(i, behaviours[i]["name"]))

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

mindist = 10.0
maxdist = 40.0

random.seed(0)
trailerAvailable = trailerAvailable == (1 | 2 | 4)

print(
    "Trailer support: {} Drunk Driver support: {}".format(
        "✔️" if trailerAvailable else "❌", "✔️" if drunkDriverAvailable else "❌"
    )
)

while True:
    if trailerAvailable:
        inp = input(
            "Enter index of Agent to spawn, t to spawn truck and trailer, r to run:"
        )
    else:
        inp = input("Enter index of Agent to spawn, r to run:")

    angle = random.uniform(0.0, 2 * math.pi)
    dist = random.uniform(mindist, maxdist)
    spawn = random.choice(spawns)
    sx = spawn.position.x
    sy = spawn.position.y
    sz = spawn.position.z
    point = lgsvl.Vector(sx + dist * math.cos(angle), sy, sz + dist * math.sin(angle))
    state = lgsvl.AgentState()
    state.transform = sim.map_point_on_lane(point)

    if inp == "r":
        print("running.")
        sim.run()

    if inp == "t" and trailerAvailable:
        truck = sim.add_agent(
            "MackAnthemStandupSleeperCab2018", lgsvl.AgentType.NPC, state
        )
        truck.follow_closest_lane(True, 5.6)
        trailer = sim.add_agent("TrailerTruckTest", lgsvl.AgentType.NPC, state)
        trailer.set_behaviour("NPCTrailerBehaviour")
        sim.remote.command(
            "agent/trailer/attach", {"trailer_uid": trailer.uid, "truck_uid": truck.uid}
        )

    else:
        try:
            agentIndex = int(inp)
            if agentIndex > len(agents):
                print("index out of range")
                continue

            agent = agents[agentIndex]["name"]
            print("Selected {}".format(agent))
            npc = sim.add_agent(agent, lgsvl.AgentType.NPC, state)

            if drunkDriverAvailable:
                inp = input("make drunk driver? yN")
            if inp == "y" or inp == "Y":
                npc.set_behaviour("NPCDrunkDriverBehaviour")
                npc.remote.command(
                    "agent/drunk/config",
                    {
                        "uid": npc.uid,
                        "correctionMinTime": 0.0,
                        "correctionMaxTime": 0.6,
                        "steerDriftMin": 0.00,
                        "steerDriftMax": 0.09,
                    },
                )

            npc.follow_closest_lane(True, 5.6)
            print("spawned agent {}, uid {}".format(agent, npc.uid))

        except ValueError:
            print("expected a number")
