#!/usr/bin/env python3
#
# Copyright (c) 2020-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl

print("Python API Quickstart #30: Using the time to collision trigger")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave, 42)

spawns = sim.get_spawn()
layer_mask = 0
layer_mask |= 1 << 0  # 0 is the layer for the road (default)

# EGO
state = lgsvl.AgentState()
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])
spawn_state = spawns[0]
hit = sim.raycast(
    spawn_state.position + forward * 40, lgsvl.Vector(0, -1, 0), layer_mask
)
spawn_state.position = hit.point
state.transform = spawn_state
state.velocity = forward * 2
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5), lgsvl.AgentType.EGO, state)

# NPC
state = lgsvl.AgentState()
npc_position = lgsvl.Vector(-4, -1, -48)
hit = sim.raycast(npc_position, lgsvl.Vector(0, -1, 0), layer_mask)
npc_rotation = lgsvl.Vector(0, 16, 0)
state.transform.position = hit.point
state.transform.rotation = npc_rotation
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

for i in range(2):
    speed = 8
    # Waypoint angles are input as Euler angles (roll, pitch, yaw)
    angle = npc_rotation
    # Raycast the points onto the ground because BorregasAve is not flat
    npc_position.x += 6
    npc_position.z += 21
    hit = sim.raycast(npc_position, lgsvl.Vector(0, -1, 0), layer_mask)

    trigger = None
    if i == 0:
        effector = lgsvl.TriggerEffector("TimeToCollision", {})
        trigger = lgsvl.WaypointTrigger([effector])
    wp = lgsvl.DriveWaypoint(
        position=hit.point,
        speed=speed,
        angle=angle,
        idle=0,
        trigger_distance=0,
        trigger=trigger,
    )
    waypoints.append(wp)


def on_waypoint(agent, index):
    print("waypoint {} reached".format(index))


def agents_traversed_waypoints():
    print("All agents traversed their waypoints.")
    sim.stop()


# The above function needs to be added to the list of callbacks for the NPC
npc.on_waypoint_reached(on_waypoint)
sim.agents_traversed_waypoints(agents_traversed_waypoints)

# The NPC needs to be given the list of waypoints.
# A bool can be passed as the 2nd argument that controls whether or not the NPC loops over the waypoints (default false)
npc.follow(waypoints)

input("Press Enter to run")

sim.run()
