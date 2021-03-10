#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl

print("Python API Quickstart #25: NPC flying to waypoints")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

spawns = sim.get_spawn()

# EGO
state = lgsvl.AgentState()
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])
up = lgsvl.utils.transform_to_up(spawns[0])
state.transform = spawns[0]
sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

# NPC
state = lgsvl.AgentState()
state.transform.position = spawns[0].position + 10 * forward
state.transform.rotation = spawns[0].rotation
npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)

# This block creates the list of waypoints that the NPC will follow
# Each waypoint consists of a position vector, speed, and an angular orientation vector
waypoints = []
z_delta = 12

layer_mask = 0
layer_mask |= 1 << 0  # 0 is the layer for the road (default)
px = 0
py = 0.5

for i in range(75):
    speed = 6
    px = 0
    py = ((i + 1) * 0.05) if (i < 50) else (50 * 0.05 + (50 - i) * 0.05)
    pz = i * z_delta * 0.05

    angle = lgsvl.Vector(i, 0, 3 * i)

    # Raycast the points onto the ground because BorregasAve is not flat
    hit = sim.raycast(
        spawns[0].position + px * right + pz * forward,
        lgsvl.Vector(0, -1, 0),
        layer_mask,
    )

    wp = lgsvl.DriveWaypoint(
        spawns[0].position + px * right + py * up + pz * forward, speed, angle, 0, 0
    )
    waypoints.append(wp)


# When the NPC is within 1m of the waypoint, this will be called
def on_waypoint(agent, index):
    print("waypoint {} reached".format(index))


# The above function needs to be added to the list of callbacks for the NPC
npc.on_waypoint_reached(on_waypoint)

# The NPC needs to be given the list of waypoints.
# A bool can be passed as the 2nd argument that controls whether or not the NPC loops over the waypoints (default false)
npc.follow(waypoints)

input("Press Enter to run the simulation for 12 seconds")

sim.run(12)
