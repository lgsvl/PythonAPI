#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

# See VF_C_25_Slow for a commented script

import time
import logging
from environs import Env
import lgsvl

FORMAT = "[%(levelname)6s] [%(name)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
log = logging.getLogger(__name__)

env = Env()

MAX_EGO_SPEED = 20.12  # (72 km/h, 45 mph)
SPEED_VARIANCE = 10  # Simple Physics does not return an accurate value
MAX_POV_SPEED = 17.88  # (64 km/h, 40 mph)
MAX_POV_ROTATION = 5  # deg/s
TIME_LIMIT = 30  # seconds
TIME_DELAY = 7
MAX_FOLLOWING_DISTANCE = 100  # Apollo 3.5 is very cautious

LGSVL__SIMULATOR_HOST = env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1")
LGSVL__SIMULATOR_PORT = env.int("LGSVL__SIMULATOR_PORT", 8181)
LGSVL__AUTOPILOT_0_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
LGSVL__AUTOPILOT_0_PORT = env.int("LGSVL__AUTOPILOT_0_PORT", 9090)

print("VF_S_45_Slow - ", end='')

sim = lgsvl.Simulator(LGSVL__SIMULATOR_HOST, LGSVL__SIMULATOR_PORT)
scene_name = env.str("LGSVL__MAP", lgsvl.wise.DefaultAssets.map_straight1lanesame)
if sim.current_scene == scene_name:
    sim.reset()
else:
    sim.load(scene_name)

# spawn EGO in the 2nd to right lane
egoState = lgsvl.AgentState()
egoState.transform = sim.map_point_on_lane(lgsvl.Vector(1, 0, 65))
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5_full_analysis), lgsvl.AgentType.EGO, egoState)
forward = lgsvl.utils.transform_to_forward(egoState.transform)
right = lgsvl.utils.transform_to_right(egoState.transform)

ego.connect_bridge(LGSVL__AUTOPILOT_0_HOST, LGSVL__AUTOPILOT_0_PORT)

dv = lgsvl.dreamview.Connection(sim, ego, LGSVL__AUTOPILOT_0_HOST)
dv.set_hd_map(env.str("LGSVL__AUTOPILOT_HD_MAP", 'Straight1LaneSame'))
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
    ]
    log.warning("LGSVL__AUTOPILOT_0_VEHICLE_MODULES is not set, using default list: {0}".format(modules))

destination = egoState.position + 135 * forward
dv.setup_apollo(destination.x, destination.z, modules)

POVState = lgsvl.AgentState()
POVState.transform = sim.map_point_on_lane(egoState.position + 68 * forward)
POV = sim.add_agent("Sedan", lgsvl.AgentType.NPC, POVState)


def on_collision(agent1, agent2, contact):
    raise lgsvl.evaluator.TestException("Ego collided with {}".format(agent2))


ego.on_collision(on_collision)
POV.on_collision(on_collision)

endOfRoad = egoState.position + 135 * forward

try:
    t0 = time.time()
    sim.run(TIME_DELAY)  # The EGO should start moving first
    POV.follow_closest_lane(True, MAX_POV_SPEED, False)
    while True:
        sim.run(0.5)
        egoCurrentState = ego.state
        if egoCurrentState.speed > MAX_EGO_SPEED + SPEED_VARIANCE:
            raise lgsvl.evaluator.TestException(
                "Ego speed exceeded limit, {} > {} m/s".format(egoCurrentState.speed, MAX_EGO_SPEED + SPEED_VARIANCE)
            )
        POVCurrentState = POV.state
        if POVCurrentState.speed > MAX_POV_SPEED + SPEED_VARIANCE:
            raise lgsvl.evaluator.TestException(
                "POV speed exceeded limit, {} > {} m/s".format(POVCurrentState.speed, MAX_POV_SPEED + SPEED_VARIANCE)
            )
        if POVCurrentState.angular_velocity.y > MAX_POV_ROTATION:
            raise lgsvl.evaluator.TestException(
                "POV angular rotation exceeded limit, {} > {} deg/s".format(
                    POVCurrentState.angular_velocity, MAX_POV_ROTATION
                )
            )
        if lgsvl.evaluator.separation(POVCurrentState.position, endOfRoad) < 5:
            break
        if time.time() - t0 > TIME_LIMIT:
            break
except lgsvl.evaluator.TestException as e:
    exit("FAILED: {}".format(e))

separation = lgsvl.evaluator.separation(egoCurrentState.position, POVCurrentState.position)
try:
    if separation > MAX_FOLLOWING_DISTANCE:
        raise lgsvl.evaluator.TestException(
            "FAILED: EGO following distance was not maintained, {} > {}".format(separation, MAX_FOLLOWING_DISTANCE)
        )
    else:
        print("PASSED")
except lgsvl.evaluator.TestException as e:
    exit("FAILED: {}".format(e))
