#!/usr/bin/env python3
#
# Copyright (c) 2019 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl
import math

sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)
if sim.current_scene == "BorregasAve":
  sim.reset()
else:
  sim.load("BorregasAve")

spawns = sim.get_spawn()

# EGO

state = lgsvl.AgentState()
state.transform = spawns[0]
a = sim.add_agent("Jaguar2015XE (Apollo 5.0)", lgsvl.AgentType.EGO, state)

# NPC, 10 meters ahead

sx = spawns[0].position.x
sy = spawns[0].position.y
sz = spawns[0].position.z + 10.0

state = lgsvl.AgentState()
state.transform = spawns[0]
state.transform.position.x = sx
state.transform.position.z = sz
npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)


# This block creates the list of waypoints that the NPC will follow
# Each waypoint consists of a position vector, speed, and an angular orientation vector
waypoints = []
x_max = 2
y_max = 2
z_delta = 12

layer_mask = 0
layer_mask |= 1 << 0 # 0 is the layer for the road (default)
px = 0
py = 0.5

for i in range(75):
  speed = 6
  px = 0
  py = ((i + 1) * 0.05) if (i < 50) else (50 * 0.05 + (50 - i) * 0.05)
  pz = i * z_delta * 0.05

  angle = lgsvl.Vector(i, 0, 3*i)

  # Raycast the points onto the ground because BorregasAve is not flat
  hit = sim.raycast(lgsvl.Vector(sx + px, sy, sz + pz), lgsvl.Vector(0,-1,0), layer_mask) 

  wp = lgsvl.DriveWaypoint(lgsvl.Vector(sx + px, sy + py, sz + pz), speed, angle, 0, 0)
  waypoints.append(wp)

# When the NPC is within 1m of the waypoint, this will be called
def on_waypoint(agent, index):
  print("waypoint {} reached".format(index))

# The above function needs to be added to the list of callbacks for the NPC
npc.on_waypoint_reached(on_waypoint)

# The NPC needs to be given the list of waypoints. 
# A bool can be passed as the 2nd argument that controls whether or not the NPC loops over the waypoints (default false)
npc.follow(waypoints)

input("Press Enter to run")

sim.run()
