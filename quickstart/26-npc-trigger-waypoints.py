#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl

print("Python API Quickstart #26: NPC triggering the waypoints callbacks")
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
state.transform = spawns[0]
state.velocity = 12 * forward
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

# NPC
state = lgsvl.AgentState()
state.transform.position = spawns[0].position + 10 * forward
state.transform.rotation = spawns[0].rotation
npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)

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
        spawns[0].position + px * right + pz * forward,
        lgsvl.Vector(0, -1, 0),
        layer_mask,
    )

    # Trigger is set to 10 meters for every other waypoint (0 means no trigger)
    tr = 0
    if i % 2:
        tr = 10
    wp = lgsvl.DriveWaypoint(
        position=hit.point, speed=speed, angle=angle, idle=0, trigger_distance=tr
    )
    waypoints.append(wp)


# When the NPC is within 0.5m of the waypoint, this will be called
def on_waypoint(agent, index):
    print("waypoint {} reached, waiting for ego to get closer".format(index))


# The above function needs to be added to the list of callbacks for the NPC
npc.on_waypoint_reached(on_waypoint)

# The NPC needs to be given the list of waypoints.
# A bool can be passed as the 2nd argument that controls whether or not the NPC loops over the waypoints (default false)
npc.follow(waypoints)

input("Press Enter to run simulation for 22 seconds")

sim.run(22)
