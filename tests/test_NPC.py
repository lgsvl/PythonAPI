#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import unittest
import time
import lgsvl
from .common import SimConnection, spawnState, cmEqual, mEqual, TestException

PROBLEM = "Object reference not set to an instance of an object"

# TODO Add tests for callbacks for when NPC changes lanes, reaches stop line


class TestNPC(unittest.TestCase):

    # THIS TEST RUNS FIRST
    def test_AAA_NPC_no_scene(self):
        with SimConnection(load_scene=False) as sim:
            with self.assertRaises(Exception) as e:
                state = lgsvl.AgentState()
                agent = sim.add_agent("Jeep", lgsvl.AgentType.NPC, state)
                agent.state.position
                self.assertFalse(repr(e.exception).startswith(PROBLEM))

    def test_NPC_creation(self):  # Check if the different types of NPCs can be created
        with SimConnection(60) as sim:
            state = spawnState(sim)
            right = lgsvl.utils.transform_to_right(state.transform)
            state.transform.position = state.position + 10 * right
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            spawns = sim.get_spawn()
            for name in ["Sedan", "SUV", "Jeep", "Hatchback", "SchoolBus", "BoxTruck"]:
                agent = self.create_NPC(sim, name)
                cmEqual(self, agent.state.position, spawns[0].position, name)
                self.assertEqual(agent.name, name)

    def test_get_agents(self):
        with SimConnection() as sim:
            agentCount = 1
            state = spawnState(sim)
            right = lgsvl.utils.transform_to_right(state.transform)
            state.transform.position = state.position + 10 * right
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            for name in ["Sedan", "SUV", "Jeep", "Hatchback", "SchoolBus", "BoxTruck"]:
                self.create_NPC(sim, name)
                agentCount += 1
            agents = sim.get_agents()
            self.assertEqual(len(agents), agentCount)
            agentCounter = {lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5:0, "Sedan":0, "SUV":0, "Jeep":0, "Hatchback":0, "SchoolBus":0, "BoxTruck":0}
            for a in agents:
                agentCounter[a.name] += 1

            expectedAgents = [lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, "Sedan", "SUV", "Jeep", "Hatchback", "SchoolBus", "BoxTruck"]
            for a in expectedAgents:
                with self.subTest(a):
                    self.assertEqual(agentCounter[a], 1)

    def test_NPC_follow_lane(self):  # Check if NPC can follow lane
        with SimConnection() as sim:
            state = spawnState(sim)
            right = lgsvl.utils.transform_to_right(state.transform)
            state.transform.position = state.position - 5 * right
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            agent = self.create_NPC(sim, "Sedan")
            agent.follow_closest_lane(True, 5.6)
            sim.run(2.0)
            agentState = agent.state
            self.assertGreater(agentState.speed, 0)
            # self.assertAlmostEqual(agent.state.speed, 5.6, delta=1)
            self.assertLess(agent.state.position.x - sim.get_spawn()[0].position.x, 5.6*2)

    def test_rotate_NPC(self):  # Check if NPC can be rotated
        with SimConnection() as sim:
            state = spawnState(sim)
            right = lgsvl.utils.transform_to_right(state.transform)
            state.transform.position = state.position - 5 * right
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            agent = self.create_NPC(sim, "SUV")
            self.assertAlmostEqual(agent.state.transform.rotation.y, 104.823394, places=3)
            x = agent.state
            x.transform.rotation.y = 10
            agent.state = x
            self.assertAlmostEqual(agent.state.transform.rotation.y, 10, delta=0.1)

    def test_blank_agent(self):  # Check that an exception is raised if a blank name is given
        with SimConnection() as sim:
            with self.assertRaises(Exception) as e:
                self.create_NPC(sim, "")
            self.assertFalse(repr(e.exception).startswith(PROBLEM))

    def test_int_agent(self):  # Check that an exception is raised if an integer name is given
        with SimConnection() as sim:
            with self.assertRaises(TypeError):
                    self.create_NPC(sim, 1)

    def test_wrong_type_NPC(self):  # Check that an exception is raised if 4 is given as the agent type
        with SimConnection() as sim:
            with self.assertRaises(TypeError):
                sim.add_agent("SUV", 4, spawnState(sim))

    def test_wrong_type_value(self):
        with SimConnection() as sim:
            with self.assertRaises(ValueError):
                sim.add_agent("SUV", lgsvl.AgentType(9), spawnState(sim))

    def test_upsidedown_NPC(self):  # Check that an upside-down NPC keeps falling
        with SimConnection() as sim:
            state = spawnState(sim)
            right = lgsvl.utils.transform_to_right(state.transform)
            state.transform.position = state.position + 10 * right
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            state = spawnState(sim)
            state.rotation.z += 180
            agent = sim.add_agent("Hatchback", lgsvl.AgentType.NPC, state)
            initial_height = agent.state.position.y
            sim.run(1)
            final_height = agent.state.position.y
            self.assertLess(final_height, initial_height)

    def test_flying_NPC(self):  # Check if an NPC created above the map falls
        with SimConnection() as sim:
            state = spawnState(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            up = lgsvl.utils.transform_to_up(state.transform)
            state.transform.position = state.position - 10 * forward + 200 * up
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            state = spawnState(sim)
            state.transform.position = state.position + 200 * up
            agent = sim.add_agent("Hatchback", lgsvl.AgentType.NPC, state)
            initial_height = agent.state.position.y
            sim.run(1)
            final_height = agent.state.position.y
            self.assertLess(final_height, initial_height)

    def test_underground_NPC(self):  # Check if an NPC created below the map keeps falling
        with SimConnection() as sim:
            state = spawnState(sim)
            up = lgsvl.utils.transform_to_up(state.transform)
            state.transform.position = state.position - 200 * up
            agent = sim.add_agent("Hatchback", lgsvl.AgentType.NPC, state)
            initial_height = agent.state.position.y
            sim.run(1)
            final_height = agent.state.position.y
            self.assertLess(final_height, initial_height)

    def test_access_removed_NPC(self):  # Check that and exception is raised when trying to access position of a removed NPC
        with SimConnection() as sim:
            state = spawnState(sim)
            agent = sim.add_agent("Hatchback", lgsvl.AgentType.NPC, state)
            self.assertAlmostEqual(agent.state.position.x, state.position.x)
            sim.remove_agent(agent)
            with self.assertRaises(Exception) as e:
                agent.state.position
            self.assertFalse(repr(e.exception).startswith(PROBLEM))

    def test_follow_waypoints(self):  # Check that the NPC can follow waypoints
        with SimConnection(60) as sim:
            state = spawnState(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            right = lgsvl.utils.transform_to_right(state.transform)
            state.transform.position = state.position - 5 * right
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            spawns = sim.get_spawn()
            agent = self.create_NPC(sim, "Sedan")

            # snake-drive
            layer_mask = 0
            layer_mask |= 1 << 0
            waypointCommands = []
            waypoints = []
            x_max = 4
            z_delta = 12
            for i in range(5):
                speed = 6 if i % 2 == 0 else 12
                pz = (i + 1) * z_delta
                px = x_max * (-1 if i % 2 == 0 else 1)

                hit = sim.raycast(spawns[0].position + pz * forward + px * right, lgsvl.Vector(0,-1,0), layer_mask)
                wp = lgsvl.DriveWaypoint(hit.point, speed)
                waypointCommands.append(wp)
                waypoints.append(hit.point)

            def on_waypoint(agent, index):
                msg = "Waypoint " + str(index)
                mEqual(self, agent.state.position, waypoints[index], msg)
                if index == len(waypoints)-1:
                    sim.stop()

            agent.on_waypoint_reached(on_waypoint)

            agent.follow(waypointCommands)

            sim.run()

    def test_high_waypoint(self):  # Check that a NPC will drive to under a high waypoint
        with SimConnection(15) as sim:
            state = spawnState(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            right = lgsvl.utils.transform_to_right(state.transform)
            up = lgsvl.utils.transform_to_up(state.transform)
            state.transform.position = state.position - 5 * right
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            spawns = sim.get_spawn()
            agent = self.create_NPC(sim, "Sedan")

            px = 4
            pz = 12
            py = 50
            speed = 6
            destination = spawns[0].position + px * right + py * up + pz * forward
            wp = [lgsvl.DriveWaypoint(destination, speed)]

            def on_waypoint(agent,index):
                sim.stop()

            agent.on_waypoint_reached(on_waypoint)
            agent.follow(wp)
            sim.run(10)

            self.assertLess((agent.state.position - destination).magnitude(), 1)

    def test_npc_different_directions(self):  # Check that specified velocities match the NPC's movement
        with SimConnection() as sim:
            state = spawnState(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            up = lgsvl.utils.transform_to_up(state.transform)
            right = lgsvl.utils.transform_to_right(state.transform)

            state.transform.position = state.position - 5 * right
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            state = spawnState(sim)
            state.velocity = -10 * right
            npc = sim.add_agent("SUV", lgsvl.AgentType.NPC, state)
            sim.run(.5)
            target = state.position - 1.8 * right
            self.assertLess((npc.state.position - target).magnitude(), 1)
            sim.remove_agent(npc)

            state.velocity = 10 * up
            npc = sim.add_agent("SUV", lgsvl.AgentType.NPC, state)
            sim.run(0.5)
            target = state.position + 3 * up
            self.assertLess((npc.state.position - target).magnitude(), 1)
            sim.remove_agent(npc)

            state.velocity = 10 * forward
            npc = sim.add_agent("SUV", lgsvl.AgentType.NPC, state)
            sim.run(0.5)
            target = state.position + 4 * forward
            self.assertLess((npc.state.position - target).magnitude(), 1)

    def test_stopline_callback(self):  # Check that the stopline call back works properly
        with self.assertRaises(TestException) as e:
            with SimConnection(60) as sim:
                state = spawnState(sim)
                npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)

                def on_stop_line(agent):
                    raise TestException("Waypoint reached")

                npc.follow_closest_lane(True, 10)
                npc.on_stop_line(on_stop_line)

                right = lgsvl.utils.transform_to_right(state.transform)

                state.transform.position = state.position - 5 * right
                sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
                sim.run(60)
        self.assertIn("Waypoint reached", repr(e.exception))

    def test_remove_npc_with_callback(self):  # Check that an NPC with callbacks is removed properly
        with SimConnection() as sim:
            npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, spawnState(sim))

            def on_stop_line(agent):
                pass

            npc.follow_closest_lane(True, 10)
            npc.on_stop_line(on_stop_line)

            sim.run(1)
            sim.remove_agent(npc)
            with self.assertRaises(Exception):
                npc.state.position
            with self.assertRaises(KeyError):
                sim.callbacks[npc]

    def test_spawn_speed(self):  # Checks that a spawned agent keeps the correct speed when spawned
        with SimConnection() as sim:
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, spawnState(sim, 1))
            npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, spawnState(sim))

            self.assertEqual(npc.state.speed,0)
            sim.run(1)
            self.assertEqual(npc.state.speed,0)

    def test_lane_change_right(self):
        with SimConnection(40) as sim:
            state = lgsvl.AgentState()
            state.transform = sim.map_point_on_lane(lgsvl.Vector(4.49, -1.57, 40.85))
            npc = sim.add_agent("SUV", lgsvl.AgentType.NPC, state)

            state.transform = sim.map_point_on_lane(lgsvl.Vector(0.63, -1.57, 42.73))
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            target = state.position + 31 * forward

            npc.follow_closest_lane(True, 10)

            agents = []

            def on_lane_change(agent):
                agents.append(agent)

            npc.on_lane_change(on_lane_change)
            sim.run(2)
            npc.change_lane(False)
            sim.run(3)

            self.assertTrue(npc == agents[0])
            self.assertAlmostEqual((npc.state.position - target).magnitude(), 0, delta=2)

    def test_lane_change_right_missing_lane(self):
        with SimConnection(40) as sim:
            state = lgsvl.AgentState()
            state.transform = sim.map_point_on_lane(lgsvl.Vector(0.63, -1.57, 42.73))
            npc = sim.add_agent("Hatchback", lgsvl.AgentType.NPC, state)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            target = state.position + 42.75 * forward

            state.transform = sim.map_point_on_lane(lgsvl.Vector(4.49, -1.57, 40.85))
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)

            npc.follow_closest_lane(True, 10)

            agents = []

            def on_lane_change(agent):
                agents.append(agent)

            npc.on_lane_change(on_lane_change)
            sim.run(2)
            npc.change_lane(False)
            sim.run(3)

            self.assertTrue(len(agents)== 0)
            self.assertAlmostEqual((npc.state.position - target).magnitude(), 0, delta=2)

    def test_lane_change_left(self):
        with SimConnection(40) as sim:
            state = lgsvl.AgentState()
            state.transform = sim.map_point_on_lane(lgsvl.Vector(4.49, -1.57, 40.85))
            npc = sim.add_agent("SUV", lgsvl.AgentType.NPC, state)

            state.transform = sim.map_point_on_lane(lgsvl.Vector(9.82, -1.79, 42.02))
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            target = state.position + 31 * forward

            npc.follow_closest_lane(True, 10)

            agents = []

            def on_lane_change(agent):
                agents.append(agent)

            npc.on_lane_change(on_lane_change)
            sim.run(2)
            npc.change_lane(True)
            sim.run(3)

            self.assertTrue(npc == agents[0])
            self.assertAlmostEqual((npc.state.position - target).magnitude(), 0, delta=2)

    def test_lane_change_left_opposing_traffic(self):
        with SimConnection(40) as sim:
            state = lgsvl.AgentState()
            state.transform = sim.map_point_on_lane(lgsvl.Vector(78.962, -3.363, -40.292))
            npc = sim.add_agent("SUV", lgsvl.AgentType.NPC, state)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            target = state.position + 42.75 * forward

            state.transform.position = state.position - 10 * forward
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)

            npc.follow_closest_lane(True, 10)

            agents = []

            def on_lane_change(agent):
                agents.append(agent)

            npc.on_lane_change(on_lane_change)
            sim.run(2)
            npc.change_lane(True)
            sim.run(3)

            self.assertTrue(len(agents) == 0)
            self.assertAlmostEqual((npc.state.position - target).magnitude(), 0, delta=2)

    @unittest.skip("No applicable location in BorregasAve")
    def test_multiple_lane_changes(self):
        with SimConnection(120) as sim:
            state = lgsvl.AgentState()
            state.transform.position = lgsvl.Vector(-180,10,239)
            state.transform.rotation = lgsvl.Vector(0,90,0)
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguae2015xe_autowareai, lgsvl.AgentType.EGO, state)

            state = lgsvl.AgentState()
            state.transform.position = lgsvl.Vector(-175, 10, 234.5)
            state.transform.rotation = lgsvl.Vector(0, 90, 0.016)
            npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)

            npc.follow_closest_lane(True, 10)

            agents = []

            def on_lane_change(agent):
                agents.append(agent)

            npc.on_lane_change(on_lane_change)
            sim.run(1)
            npc.change_lane(True)
            sim.run(10)
            self.assertTrue(len(agents) == 1)
            self.assertTrue(npc == agents[0])
            self.assertAlmostEqual(npc.state.position.x, 238.5, delta=1.5)

            npc.change_lane(True)
            sim.run(13)
            self.assertTrue(len(agents) == 2)
            self.assertTrue(npc == agents[1])
            self.assertAlmostEqual(npc.state.position.x, 242.5, delta=1.5)

            npc.change_lane(False)
            sim.run(10)
            self.assertTrue(len(agents) == 3)
            self.assertTrue(npc == agents[2])
            self.assertAlmostEqual(npc.state.position.x, 238.5, delta=1.5)

    def test_set_lights_exceptions(self):
        with SimConnection() as sim:
            npc = self.create_NPC(sim, "Sedan")
            control = lgsvl.NPCControl()
            control.headlights = 2
            npc.apply_control(control)

            with self.assertRaises(ValueError):
                control.headlights = 15
                npc.apply_control(control)

    def test_npc_control_exceptions(self):
        with SimConnection() as sim:
            npc = self.create_NPC(sim, "Hatchback")
            control = "LG SVL Simulator"

            with self.assertRaises(TypeError):
                npc.apply_control(control)

    def test_e_stop(self):
        with SimConnection(60) as sim:
            state = lgsvl.AgentState()
            state.transform = sim.map_point_on_lane(lgsvl.Vector(78.962, -3.363, -40.292))
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            state.transform.position = state.position + 10 * forward
            npc = sim.add_agent("Jeep", lgsvl.AgentType.NPC, state)
            npc.follow_closest_lane(True, 10)
            sim.run(2)
            self.assertGreater(npc.state.speed, 0)
            control = lgsvl.NPCControl()
            control.e_stop = True
            npc.apply_control(control)
            sim.run(2)
            self.assertAlmostEqual(npc.state.speed, 0, delta=0.01)
            control.e_stop = False
            npc.apply_control(control)
            sim.run(2)
            self.assertGreater(npc.state.speed, 0)

    def test_waypoint_speed(self):
        with SimConnection(60) as sim:
            state = lgsvl.AgentState()
            state.transform = sim.map_point_on_lane(lgsvl.Vector(78.962, -3.363, -40.292))
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            up = lgsvl.utils.transform_to_up(state.transform)
            state.transform.position = state.position + 10 * forward
            npc = sim.add_agent("Hatchback", lgsvl.AgentType.NPC, state)
            waypoints = []

            layer_mask = 0
            layer_mask |= 1 << 0

            hit = sim.raycast(state.position + 10 * forward + 50 * up, lgsvl.Vector(0,-1,0), layer_mask)
            waypoints.append(lgsvl.DriveWaypoint(hit.point, 5, lgsvl.Vector(0,0,0), 0, 0)) # this waypoint to allow NPC to get up to speed

            hit = sim.raycast(state.position + 30 * forward + 50 * up, lgsvl.Vector(0,-1,0), layer_mask)
            waypoints.append(lgsvl.DriveWaypoint(hit.point, 5, lgsvl.Vector(0,0,0), 0, 0))

            def on_waypoint(agent, index):
                sim.stop()

            npc.on_waypoint_reached(on_waypoint)
            npc.follow(waypoints)

            sim.run()
            t0 = time.time()
            sim.run()
            t1 = time.time()
            waypoints = []
            hit = sim.raycast(state.position + 40 * forward + 50 * up, lgsvl.Vector(0,-1,0), layer_mask)
            waypoints.append(lgsvl.DriveWaypoint(hit.point, 20, lgsvl.Vector(0,0,0), 0, 0)) # this waypoint to allow NPC to get up to speed
            hit = sim.raycast(state.position + 120 * forward + 50 * up, lgsvl.Vector(0,-1,0), layer_mask)
            waypoints.append(lgsvl.DriveWaypoint(hit.point, 20, lgsvl.Vector(0,0,0), 0, 0))
            npc.follow(waypoints)
            sim.run()
            t2 = time.time()
            sim.run()
            t3 = time.time()
            lowSpeed = t1-t0
            highSpeed = t3-t2
            self.assertAlmostEqual(lowSpeed, highSpeed, delta=0.5)
            self.assertAlmostEqual(lowSpeed, 4.5, delta=0.5)
            self.assertAlmostEqual(highSpeed, 4.5, delta=0.5)

    # def test_physics_mode(self):
    #     with SimConnection(60) as sim:
    #         sim.add_agent("XE_Rigged-apollo_3_5", lgsvl.AgentType.EGO, spawnState(sim, 1))
    #         npc = self.create_NPC(sim, "Sedan")
    #         npc.follow_closest_lane(True, 8, False)
    #         sim.run(2)
    #         self.assertAlmostEqual(npc.state.speed, 8, delta=1)
    #         sim.set_physics(False)
    #         sim.run(2)
    #         self.assertGreater(npc.state.speed, 0)
    #         sim.set_physics(True)
    #         sim.run(2)
    #         self.assertAlmostEqual(npc.state.speed, 8, delta=1)

    def create_NPC(self, sim, name):  # Create the specified NPC
        return sim.add_agent(name, lgsvl.AgentType.NPC, spawnState(sim))
