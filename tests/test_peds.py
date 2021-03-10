#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import unittest
import math

import lgsvl
from .common import SimConnection, cmEqual, mEqual, spawnState


class TestPeds(unittest.TestCase):
    def test_ped_creation(self):  # Check if the different types of Peds can be created
        with SimConnection() as sim:
            state = spawnState(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            state.transform.position = state.position - 4 * forward
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            for name in ["Bob", "EntrepreneurFemale", "Howard", "Johny", \
                "Pamela", "Presley", "Robin", "Stephen", "Zoe"]:
                agent = self.create_ped(sim, name, spawnState(sim))
                cmEqual(self, agent.state.position, sim.get_spawn()[0].position, name)
                self.assertEqual(agent.name, name)

    def test_ped_random_walk(self):  # Check if pedestrians can walk randomly
        with SimConnection(40) as sim:
            state = spawnState(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            state.transform.position = state.position - 4 * forward
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            state = spawnState(sim)
            spawnPoint = state.transform.position

            bob = self.create_ped(sim, "Bob", state)
            bob.walk_randomly(True)
            sim.run(2)

            randPoint = bob.transform.position
            self.assertNotAlmostEqual(spawnPoint.x, randPoint.x)
            self.assertNotAlmostEqual(spawnPoint.y, randPoint.y)
            self.assertNotAlmostEqual(spawnPoint.z, randPoint.z)

            bob.walk_randomly(False)
            sim.run(2)

            cmEqual(self, randPoint, bob.state.transform.position, "Ped random walk")

    def test_ped_circle_waypoints(self):  # Check if pedestrians can follow waypoints
        with SimConnection(60) as sim:
            state = spawnState(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            right = lgsvl.utils.transform_to_right(state.transform)
            state.transform.position = state.position - 4 * forward
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            state = spawnState(sim)
            state.transform.position = state.position + 10 * forward
            radius = 5
            count = 3
            waypointCommands = []
            waypoints = []
            layer_mask = 0 | (1 << 0)
            for i in range(count):
                x = radius * math.cos(i * 2 * math.pi / count)
                z = radius * math.sin(i * 2 * math.pi / count)
                idle = 1 if i < count//2 else 0
                hit = sim.raycast(state.position + z * forward + x * right, lgsvl.Vector(0, -1, 0), layer_mask)
                waypointCommands.append(lgsvl.WalkWaypoint(hit.point, idle))
                waypoints.append(hit.point)

            state.transform.position = waypoints[0]
            zoe = self.create_ped(sim, "Zoe", state)

            def on_waypoint(agent,index):
                msg = "Waypoint " + str(index)
                mEqual(self, zoe.state.position, waypoints[index], msg)
                if index == len(waypoints)-1:
                    sim.stop()

            zoe.on_waypoint_reached(on_waypoint)
            zoe.follow(waypointCommands, True)
            sim.run()

    def test_waypoint_idle_time(self):
        with SimConnection(60) as sim:
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, spawnState(sim))
            state = spawnState(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            right = lgsvl.utils.transform_to_right(state.transform)
            state.transform.position = state.position + 10 * forward
            zoe = self.create_ped(sim, "Zoe", state)

            def on_waypoint(agent, index):
                sim.stop()

            layer_mask = 0 | (1 << 0)
            waypoints = []
            hit = sim.raycast(state.position - 2 * right, lgsvl.Vector(0, -1, 0), layer_mask)
            waypoints.append(lgsvl.WalkWaypoint(hit.point, 0))
            hit = sim.raycast(state.position - 5 * right, lgsvl.Vector(0, -1, 0), layer_mask)
            waypoints.append(lgsvl.WalkWaypoint(hit.point, 0))

            zoe.on_waypoint_reached(on_waypoint)
            zoe.follow(waypoints)
            t0 = sim.current_time
            sim.run() # reach the first waypoint
            sim.run() # reach the second waypoint
            t1 = sim.current_time
            noIdleTime = t1-t0

            zoe.state = state
            waypoints = []
            hit = sim.raycast(state.position - 2 * right, lgsvl.Vector(0, -1, 0), layer_mask)
            waypoints.append(lgsvl.WalkWaypoint(hit.point, 2))
            hit = sim.raycast(state.position - 5 * right, lgsvl.Vector(0, -1, 0), layer_mask)
            waypoints.append(lgsvl.WalkWaypoint(hit.point, 0))
            zoe.follow(waypoints)
            t2 = sim.current_time
            sim.run() # reach the first waypoint
            sim.run() # reach the second waypoint
            t3 = sim.current_time
            idleTime = t3-t2

            self.assertAlmostEqual(idleTime-noIdleTime, 2.0, delta=0.5)

    def create_ped(self, sim, name, state):  # create the specified Pedestrian
        return sim.add_agent(name, lgsvl.AgentType.PEDESTRIAN, state)
