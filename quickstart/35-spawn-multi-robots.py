#!/usr/bin/env python3
#
# Copyright (c) 2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import time
from environs import Env
import lgsvl

print("Python API Quickstart #35: Spawning multi robots with bridge connections")
env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))

map_seocho = lgsvl.wise.DefaultAssets.map_lgseocho
robots = [
    lgsvl.wise.DefaultAssets.ego_lgcloi_navigation2_multi_robot1,
    lgsvl.wise.DefaultAssets.ego_lgcloi_navigation2_multi_robot2,
    lgsvl.wise.DefaultAssets.ego_lgcloi_navigation2_multi_robot3,
]

if sim.current_scene == map_seocho:
    sim.reset()
else:
    sim.load(map_seocho)

spawns = sim.get_spawn()
spawn = spawns[1]
right = lgsvl.utils.transform_to_right(spawn)

for i, robot in enumerate(robots):
    state = lgsvl.AgentState()
    state.transform.position = spawn.position + (1.0 * i * right)
    state.transform.rotation = spawn.rotation
    ego = sim.add_agent(robot, lgsvl.AgentType.EGO, state)
    print("Spawned a robot at:", state.transform.position)

    ego.connect_bridge(env.str("LGSVL__AUTOPILOT_0_HOST", lgsvl.wise.SimulatorSettings.bridge_host), env.int("LGSVL__AUTOPILOT_0_PORT", lgsvl.wise.SimulatorSettings.bridge_port))
    print("Waiting for connection...")
    while not ego.bridge_connected:
        time.sleep(1)

    print("Bridge connected:", ego.bridge_connected)

print("Running the simulation...")
sim.run()
