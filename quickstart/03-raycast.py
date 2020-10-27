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

# The next few lines spawns an EGO vehicle in the map
spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
forward = lgsvl.utils.transform_to_forward(state.transform)
right = lgsvl.utils.transform_to_right(state.transform)
up = lgsvl.utils.transform_to_up(state.transform)
sim.add_agent(env.str("LGSVL__VEHICLE_0", "Lincoln2017MKZ (Apollo 5.0)"), lgsvl.AgentType.EGO, state)

# This is the point from which the rays will originate from. It is raised 1m from the ground
p = spawns[0].position
p.y += 1

# use layers property to get all layers used in simulator
# useful bits in layer mask
# 0 - Default (road & ground)
# 9 - EGO vehicles
# 10 - NPC vehicles
# 11 - Pedestrian
# 12 - Obstacle
layers = sim.layers
print(layers)

# Included layers can be hit by the rays. Otherwise the ray will go through the layer
layer_mask = 0
tohitlayers = ["Default", "NPC", "Pedestrian", "Obstacle"]
for layer in tohitlayers:
    layer_mask |= 1 << layers[layer]

# raycast returns None if the ray doesn't collide with anything
# hit also has the point property which is the Unity position vector of where the ray collided with something
hit = sim.raycast(p, right, layer_mask)
if hit:
    print("Distance right:", hit.distance)

hit = sim.raycast(p, -right, layer_mask)
if hit:
    print("Distance left:", hit.distance)

hit = sim.raycast(p, -forward, layer_mask)
if hit:
    print("Distance back:", hit.distance)

hit = sim.raycast(p, forward, layer_mask)
if hit:
    print("Distance forward:", hit.distance)

hit = sim.raycast(p, up, layer_mask)
if hit:
    print("Distance up:", hit.distance)

hit = sim.raycast(p, -up, layer_mask)
if hit:
    print("Distance down:", hit.distance)
