#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

# This scenario simulates a situation where the EGO needs to change lanes in the presence of other traffic
# The speed limit of the scenario may require the HD map or Apollo's planning configuration to be editted which is out of the scope of this script.

# LGSVL__SIMULATOR_HOST and LGSVL__AUTOPILOT_0_HOST environment variables need to be set. The default for both is 127.0.0.1 (localhost).
# The scenario assumes that the EGO's destination is ahead in the right lane.

# POV = Principal Other Vehicle (NPC)

import time
import logging
from environs import Env
import lgsvl

FORMAT = "[%(levelname)6s] [%(name)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
log = logging.getLogger(__name__)

env = Env()

MAX_SPEED = 6.667 # (24 km/h, 15 mph) Max speed of EGO and POVs
SPEED_VARIANCE = 4 # Without real physics, the calculation for a rigidbody's velocity is very imprecise
MAX_POV_SEPARATION = 13 # The POVs in the right lane should keep a constant distance between them
SEPARATION_VARIANCE = 2 # The allowable variance in the POV separation
TIME_LIMIT = 15 # seconds

LGSVL__SIMULATOR_HOST = env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1")
LGSVL__SIMULATOR_PORT = env.int("LGSVL__SIMULATOR_PORT", 8181)
LGSVL__AUTOPILOT_0_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
LGSVL__AUTOPILOT_0_PORT = env.int("LGSVL__AUTOPILOT_0_PORT", 9090)

print("PLC_SN_15 - ", end='')

sim = lgsvl.Simulator(LGSVL__SIMULATOR_HOST, LGSVL__SIMULATOR_PORT)
scene_name = env.str("LGSVL__MAP", lgsvl.wise.DefaultAssets.map_straight2lanesame)
if sim.current_scene == scene_name:
    sim.reset()
else:
    sim.load(scene_name)

# spawn EGO in the 2nd to right lane
egoState = lgsvl.AgentState()
# A point close to the desired lane was found in Editor.
# This method returns the position and orientation of the closest lane to the point.
egoState.transform = sim.map_point_on_lane(lgsvl.Vector(3.68, 0, -50))
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5_full_analysis), lgsvl.AgentType.EGO, egoState)
forward = lgsvl.utils.transform_to_forward(egoState.transform)
right = lgsvl.utils.transform_to_right(egoState.transform)

ego.connect_bridge(LGSVL__AUTOPILOT_0_HOST, LGSVL__AUTOPILOT_0_PORT)

dv = lgsvl.dreamview.Connection(sim, ego, LGSVL__AUTOPILOT_0_HOST)  # Create the websocket connection to Dreamview
dv.set_hd_map(env.str("LGSVL__AUTOPILOT_HD_MAP", 'Straight2LaneSame'))  # Set the HD map in Dreamview
# Set the Vehicle configuration in Dreamview
dv.set_vehicle(env.str("LGSVL__AUTOPILOT_0_VEHICLE_CONFIG", 'Lincoln2017MKZ'))

try:
    modules = env.list("LGSVL__AUTOPILOT_0_VEHICLE_MODULES", subcast=str)
    if len(modules) == 0:
        log.warning("LGSVL__AUTOPILOT_0_VEHICLE_MODULES is empty, using default list: {0}".format(modules))
        modules = [
            'Recorder',
            'Localization',
            'Perception',
            'Transform',
            'Routing',
            'Prediction',
            'Planning',
            'Traffic Light',
            'Control'
        ]
except Exception:
    modules = [
        'Recorder',
        'Localization',
        'Perception',
        'Transform',
        'Routing',
        'Prediction',
        'Planning',
        'Traffic Light',
        'Control'
    ]  # The list of modules to be enabled
    log.warning("LGSVL__AUTOPILOT_0_VEHICLE_MODULES is not set, using default list: {0}".format(modules))

# This is an lgsvl.Vector with the coordinates of the destination in the Unity coordinate system
destination = egoState.position + 120 * forward + 3.6 * right
# Will enable all the modules and then wait for Apollo to be ready before continuing
dv.setup_apollo(destination.x, destination.z, modules)

# The first POV is positioned such that its rear bumper is 5m in front of the EGO's front bumper in the right lane
POV1State = lgsvl.AgentState()
# 5m ahead of EGO, +5m because the transforms are the centers of the models
POV1State.transform = sim.map_point_on_lane(egoState.position + 10 * forward + 3.6 * right)
POV1 = sim.add_agent("Sedan", lgsvl.AgentType.NPC, POV1State)
POV1.follow_closest_lane(True, MAX_SPEED, False)

# The second POV is positioned such that its front bumper is even with the EGO's front bumper in the right lane
POV2State = lgsvl.AgentState()
POV2State.transform = sim.map_point_on_lane(egoState.position + 3.6 * right)
POV2 = sim.add_agent("Sedan", lgsvl.AgentType.NPC, POV2State)
POV2.follow_closest_lane(True, MAX_SPEED, False)

# The third POV is positioned such that its front bumper is 8m behind the EGO's rear bumper in the same lane as the EGO
POV3State = lgsvl.AgentState()
POV3State.transform = sim.map_point_on_lane(egoState.position - 13 * forward + 3.6 * right)
POV3 = sim.add_agent("Sedan", lgsvl.AgentType.NPC, POV3State)
POV3.follow_closest_lane(True, MAX_SPEED, False)


# Any collision results in a failed test
def on_collision(agent1, agent2, contact):
    raise lgsvl.evaluator.TestException("{} collided with {}".format(agent1, agent2))


ego.on_collision(on_collision)
POV1.on_collision(on_collision)
POV2.on_collision(on_collision)
POV3.on_collision(on_collision)

endOfRoad = egoState.position + 120 * forward + 3.6 * right

try:
    t0 = time.time()
    while True:
        # The EGO should not exceed the max specified speed
        egoCurrentState = ego.state
        if egoCurrentState.speed > MAX_SPEED + SPEED_VARIANCE:
            raise lgsvl.evaluator.TestException(
                "Ego speed exceeded limit, {} > {} m/s".format(egoCurrentState.speed, MAX_SPEED + SPEED_VARIANCE)
            )
        POV1CurrentState = POV1.state
        POV2CurrentState = POV2.state
        POV3CurrentState = POV3.state
        # The POVs in the right lane should maintain their starting separation
        POVSeparation = lgsvl.evaluator.separation(POV1CurrentState.position, POV2CurrentState.position)
        if POVSeparation > MAX_POV_SEPARATION + SEPARATION_VARIANCE:
            raise lgsvl.evaluator.TestException(
                "POV1 and POV2 are too far apart: {} > {}".format(POVSeparation, MAX_POV_SEPARATION + SEPARATION_VARIANCE)
            )
        # The POVs should not exceed the speed limit
        if POV1CurrentState.speed > MAX_SPEED + SPEED_VARIANCE:
            raise lgsvl.evaluator.TestException(
                "POV1 speed exceeded limit, {} > {} m/s".format(POV1CurrentState.speed, MAX_SPEED + SPEED_VARIANCE)
            )
        if POV2CurrentState.speed > MAX_SPEED + SPEED_VARIANCE:
            raise lgsvl.evaluator.TestException(
                "POV2 speed exceeded limit, {} > {} m/s".format(POV2CurrentState.speed, MAX_SPEED + SPEED_VARIANCE)
            )
        if POV3CurrentState.speed > MAX_SPEED + SPEED_VARIANCE:
            raise lgsvl.evaluator.TestException("POV3 speed exceeded limit, {} > {} m/s".format(POV3CurrentState.speed, MAX_SPEED + SPEED_VARIANCE))
        # Stops the test when the first POV reaches the end of the road
        if lgsvl.evaluator.separation(POV1CurrentState.position, endOfRoad) < 5:
            break
        # The above checks are made every 0.5 seconds.
        sim.run(0.5)
        if time.time() - t0 > TIME_LIMIT:
            break
except lgsvl.evaluator.TestException as e:
    exit("FAILED: {}".format(e))

# This checks that the EGO actually changed lanes
finalEgoState = ego.state
try:
    if lgsvl.evaluator.right_lane_check(sim, finalEgoState.transform):
        print("PASSED")
    else:
        raise lgsvl.evaluator.TestException("Ego did not change lanes")
except lgsvl.evaluator.TestException as e:
    exit("FAILED: {}".format(e))
