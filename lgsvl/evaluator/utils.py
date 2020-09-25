#
# Copyright (c) 2020 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import lgsvl
import numpy


class TestException(Exception):
    pass


def right_lane_check(simulator, ego_transform):
    egoLane = simulator.map_point_on_lane(ego_transform.position)
    right = lgsvl.utils.transform_to_right(ego_transform)
    rightLane = simulator.map_point_on_lane(ego_transform.position + 3.6 * right)

    return almost_equal(egoLane.position.x, rightLane.position.x) and \
        almost_equal(egoLane.position.y, rightLane.position.y) and \
        almost_equal(egoLane.position.z, rightLane.position.z)


def in_parking_zone(beginning, end, ego_transform):
    forward = lgsvl.utils.transform_to_forward(ego_transform)
    b2e = ego_transform.position - beginning  # Vector from beginning of parking zone to EGO's position
    b2e = b2e * (1 / b2e.magnitude())  # Make it a Unit vector to simplify dot product result
    e2e = end - ego_transform.position  # Vector from EGO's position to end of parking zone
    e2e = e2e * (1 / e2e.magnitude())
    return (
        numpy.dot([forward.x, forward.y, forward.z], [b2e.x, b2e.y, b2e.z]) > 0.9
        and numpy.dot([forward.x, forward.y, forward.z], [e2e.x, e2e.y, e2e.z]) > 0.9
    )


def almost_equal(a, b, diff=0.5):
    return abs(a - b) <= diff


def separation(V1, V2):
    return (V1 - V2).magnitude()
