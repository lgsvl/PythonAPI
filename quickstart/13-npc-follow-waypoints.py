#!/usr/bin/env python3
#
# Copyright (c) 2019-2020 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import copy
from environs import Env
import lgsvl

env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))
if sim.current_scene == "BorregasAve":
    sim.reset()
else:
    sim.load("BorregasAve")

spawns = sim.get_spawn()
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])

# Creating state object to define state for Ego and NPC
state = lgsvl.AgentState()
state.transform = spawns[0]

# Ego
ego_state = copy.deepcopy(state)
ego_state.transform.position += 50 * forward
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", "Lincoln2017MKZ (Apollo 5.0)"), lgsvl.AgentType.EGO, state)

# NPC
npc_state = copy.deepcopy(state)
npc_state.transform.position += 10 * forward
npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, npc_state)

vehicles = {
    ego: "EGO",
    npc: "Sedan",
}


# Executed upon receiving collision callback -- NPC is expected to drive through colliding objects
def on_collision(agent1, agent2, contact):
    name1 = vehicles[agent1]
    name2 = vehicles[agent2] if agent2 is not None else "OBSTACLE"
    print("{} collided with {}".format(name1, name2))


ego.on_collision(on_collision)
npc.on_collision(on_collision)

# This block creates the list of waypoints that the NPC will follow
# Each waypoint is an position vector paired with the speed that the NPC will drive to it
waypoints = []
x_max = 2
z_delta = 12

layer_mask = 0
layer_mask |= 1 << 0  # 0 is the layer for the road (default)

for i in range(20):
    speed = 24  # if i % 2 == 0 else 12
    px = 0
    pz = (i + 1) * z_delta
    # Waypoint angles are input as Euler angles (roll, pitch, yaw)
    angle = spawns[0].rotation
    # Raycast the points onto the ground because BorregasAve is not flat
    hit = sim.raycast(
        spawns[0].position + pz * forward, lgsvl.Vector(0, -1, 0), layer_mask
    )

    # NPC will wait for 1 second at each waypoint
    wp = lgsvl.DriveWaypoint(hit.point, speed, angle, 1)
    waypoints.append(wp)


# When the NPC is within 0.5m of the waypoint, this will be called
def on_waypoint(agent, index):
    print("waypoint {} reached".format(index))


# The above function needs to be added to the list of callbacks for the NPC
npc.on_waypoint_reached(on_waypoint)

# The NPC needs to be given the list of waypoints.
# A bool can be passed as the 2nd argument that controls whether or not the NPC loops over the waypoints (default false)
npc.follow(waypoints)

input("Press Enter to run\n")

sim.run()
