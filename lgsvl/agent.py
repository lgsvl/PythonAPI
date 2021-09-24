#
# Copyright (c) 2019-2020 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from .geometry import Vector, BoundingBox, Transform
from .sensor import Sensor
from .utils import accepts, ObjectState as AgentState

from enum import Enum
from collections.abc import Iterable, Callable
import json


class DriveWaypoint:
    def __init__(
        self,
        position,
        speed,
        acceleration=0,
        angle=Vector(0, 0, 0),
        idle=0,
        deactivate=False,
        trigger_distance=0,
        timestamp=-1,
        trigger=None,
    ):
        self.position = position
        self.speed = speed
        self.acceleration = acceleration
        self.angle = angle
        self.idle = idle
        self.deactivate = deactivate
        self.trigger_distance = trigger_distance
        self.timestamp = timestamp
        self.trigger = trigger


class WalkWaypoint:
    def __init__(self, position, idle, trigger_distance=0, speed=1, acceleration=0, trigger=None):
        self.position = position
        self.speed = speed
        self.acceleration = acceleration
        self.idle = idle
        self.trigger_distance = trigger_distance
        self.trigger = trigger


class WaypointTrigger:
    def __init__(self, effectors):
        self.effectors = effectors

    @staticmethod
    def from_json(j):
        return WaypointTrigger(json.loads(j["effectors"]))

    def to_json(self):
        effectors_json = []
        for effector in self.effectors:
            effectors_json.append(effector.to_json())
        return {"effectors": effectors_json}


class TriggerEffector:
    def __init__(self, type_name, parameters):
        self.type_name = type_name
        self.parameters = parameters

    @staticmethod
    def from_json(j):
        return TriggerEffector(j["type_name"], j["parameters"])

    def to_json(self):
        return {"type_name": self.type_name, "parameters": self.parameters}


class AgentType(Enum):
    EGO = 1
    NPC = 2
    PEDESTRIAN = 3


class VehicleControl:
    def __init__(self):
        self.steering = 0.0  # [-1..+1]
        self.throttle = 0.0  # [0..1]
        self.braking = 0.0  # [0..1]
        self.reverse = False
        self.handbrake = False

        # optional
        self.headlights = None  # int, 0=off, 1=low, 2=high beams
        self.windshield_wipers = None  # int, 0=off, 1-3=on
        self.turn_signal_left = None  # bool
        self.turn_signal_right = None  # bool


class NPCControl:
    def __init__(self):
        self.headlights = None  # int, 0=off, 1=low, 2=high
        self.hazards = None  # bool
        self.e_stop = None  # bool
        self.turn_signal_left = None  # bool
        self.turn_signal_right = None  # bool


class Agent:
    def __init__(self, uid, simulator):
        self.uid = uid
        self.remote = simulator.remote
        self.simulator = simulator

    @property
    def state(self):
        j = self.remote.command("agent/state/get", {"uid": self.uid})
        return AgentState.from_json(j)

    @state.setter
    @accepts(AgentState)
    def state(self, state):
        self.remote.command(
            "agent/state/set", {"uid": self.uid, "state": state.to_json()}
        )

    @property
    def transform(self):
        return self.state.transform

    @property
    def bounding_box(self):
        j = self.remote.command("agent/bounding_box/get", {"uid": self.uid})
        return BoundingBox.from_json(j)

    def __eq__(self, other):
        return self.uid == other.uid

    def __hash__(self):
        return hash(self.uid)

    @accepts(Callable)
    def on_collision(self, fn):
        self.remote.command("agent/on_collision", {"uid": self.uid})
        self.simulator._add_callback(self, "collision", fn)

    @staticmethod
    def create(simulator, uid, agent_type):
        if agent_type == AgentType.EGO:
            return EgoVehicle(uid, simulator)
        elif agent_type == AgentType.NPC:
            return NpcVehicle(uid, simulator)
        elif agent_type == AgentType.PEDESTRIAN:
            return Pedestrian(uid, simulator)
        else:
            raise ValueError("unsupported agent type")


class Vehicle(Agent):
    def __init__(self, uid, simulator):
        super().__init__(uid, simulator)


class EgoVehicle(Vehicle):
    def __init__(self, uid, simulator):
        super().__init__(uid, simulator)

    @property
    def bridge_connected(self):
        return self.remote.command("vehicle/bridge/connected", {"uid": self.uid})

    @accepts(str, int)
    def connect_bridge(self, address, port):
        if port <= 0 or port > 65535:
            raise ValueError("port value is out of range")
        self.remote.command(
            "vehicle/bridge/connect",
            {"uid": self.uid, "address": address, "port": port},
        )

    def get_bridge_type(self):
        return self.remote.command("vehicle/bridge/type", {"uid": self.uid})

    def get_sensors(self):
        j = self.remote.command("vehicle/sensors/get", {"uid": self.uid})
        return [Sensor.create(self.remote, sensor) for sensor in j]

    @accepts(bool, float)
    def set_fixed_speed(self, isCruise, speed=None):
        self.remote.command(
            "vehicle/set_fixed_speed",
            {"uid": self.uid, "isCruise": isCruise, "speed": speed},
        )

    @accepts(VehicleControl, bool)
    def apply_control(self, control, sticky=False):
        args = {
            "uid": self.uid,
            "sticky": sticky,
            "control": {
                "steering": control.steering,
                "throttle": control.throttle,
                "braking": control.braking,
                "reverse": control.reverse,
                "handbrake": control.handbrake,
            },
        }
        if control.headlights is not None:
            args["control"]["headlights"] = control.headlights
        if control.windshield_wipers is not None:
            args["control"]["windshield_wipers"] = control.windshield_wipers
        if control.turn_signal_left is not None:
            args["control"]["turn_signal_left"] = control.turn_signal_left
        if control.turn_signal_right is not None:
            args["control"]["turn_signal_right"] = control.turn_signal_right
        self.remote.command("vehicle/apply_control", args)

    def on_custom(self, fn):
        self.simulator._add_callback(self, "custom", fn)

    def set_initial_pose(self):
        self.remote.command(
            "vehicle/set_initial_pose",
            {
                "uid": self.uid,
            }
        )

    @accepts(Transform)
    def set_destination(self, transform):
        self.remote.command(
            "vehicle/set_destination",
            {
                "uid": self.uid,
                "transform": transform.to_json(),
            }
        )

    def on_destination_reached(self, fn):
        self.remote.command("agent/on_destination_reached", {"uid": self.uid})
        self.simulator._add_callback(self, "destination_reached", fn)


class NpcVehicle(Vehicle):
    def __init__(self, uid, simulator):
        super().__init__(uid, simulator)

    @accepts(Iterable, bool, str)
    def follow(self, waypoints, loop=False, waypoints_path_type="Linear"):
        """Tells the NPC to follow the waypoints

        When an NPC reaches a waypoint, it will:
        1. Wait for an EGO vehicle to approach to within the trigger_distance [meters] (ignored if 0)
        2. Wait the idle time (ignored if 0)
        3. Drive to the next waypoint (if any)

        Parameters
        ----------
        waypoints : list of DriveWaypoints
        DriveWaypoint : Class (position, speed, acceleration, angle, idle, trigger_distance)

            position : lgsvl.Vector()
            Unity coordinates of waypoint

            speed : float
            how fast the NPC should drive to the waypoint

            acceleration : float
            how fast the NPC will increase the speed

            angle : lgsvl.Vector()
            Unity rotation of the NPC at the waypoint

            idle : float
            time for the NPC to wait at the waypoint

            deactivate : bool
            whether the NPC is to deactivate while waiting at this waypoint

            trigger_distance : float
            how close an EGO must approach for the NPC to continue

            trigger : Class (list of Effectors)
            trigger data with effectors applied on this waypoint
                effectors : Class (type, value)
                typeName : string
                    effector type name
                parameters : dictionary
                    parameters of the effector (for example "value", "max_distance", "radius")

        loop : bool
        whether the NPC should loop through the waypoints after reaching the final one

        waypoints_path_type : string
        how the waypoints path should be interpreted, default path type is "Linear"
        """
        self.remote.command(
            "vehicle/follow_waypoints",
            {
                "uid": self.uid,
                "waypoints": [
                    {
                        "position": wp.position.to_json(),
                        "speed": wp.speed,
                        "acceleration": wp.acceleration,
                        "angle": wp.angle.to_json(),
                        "idle": wp.idle,
                        "deactivate": wp.deactivate,
                        "trigger_distance": wp.trigger_distance,
                        "timestamp": wp.timestamp,
                        "trigger": (
                            None if wp.trigger is None else wp.trigger.to_json()
                        ),
                    }
                    for wp in waypoints
                ],
                "waypoints_path_type": waypoints_path_type,
                "loop": loop,
            },
        )

    def follow_closest_lane(self, follow, max_speed, isLaneChange=True):
        self.remote.command(
            "vehicle/follow_closest_lane",
            {
                "uid": self.uid,
                "follow": follow,
                "max_speed": max_speed,
                "isLaneChange": isLaneChange,
            },
        )

    def set_behaviour(self, behaviour):
        self.remote.command(
            "vehicle/behaviour", {"uid": self.uid, "behaviour": behaviour}
        )

    @accepts(bool)
    def change_lane(self, isLeftChange):
        self.remote.command(
            "vehicle/change_lane", {"uid": self.uid, "isLeftChange": isLeftChange}
        )

    @accepts(NPCControl)
    def apply_control(self, control):
        args = {"uid": self.uid, "control": {}}
        if control.headlights is not None:
            if control.headlights not in [0, 1, 2]:
                raise ValueError("unsupported intensity value")
            args["control"]["headlights"] = control.headlights
        if control.hazards is not None:
            args["control"]["hazards"] = control.hazards
        if control.e_stop is not None:
            args["control"]["e_stop"] = control.e_stop
        if (
            control.turn_signal_left is not None
            or control.turn_signal_right is not None
        ):
            args["control"]["isLeftTurnSignal"] = control.turn_signal_left
            args["control"]["isRightTurnSignal"] = control.turn_signal_right
        self.remote.command("vehicle/apply_npc_control", args)

    def on_waypoint_reached(self, fn):
        self.remote.command("agent/on_waypoint_reached", {"uid": self.uid})
        self.simulator._add_callback(self, "waypoint_reached", fn)

    def on_stop_line(self, fn):
        self.remote.command("agent/on_stop_line", {"uid": self.uid})
        self.simulator._add_callback(self, "stop_line", fn)

    def on_lane_change(self, fn):
        self.remote.command("agent/on_lane_change", {"uid": self.uid})
        self.simulator._add_callback(self, "lane_change", fn)


class Pedestrian(Agent):
    def __init__(self, uid, simulator):
        super().__init__(uid, simulator)

    @accepts(bool)
    def walk_randomly(self, enable):
        self.remote.command(
            "pedestrian/walk_randomly", {"uid": self.uid, "enable": enable}
        )

    @accepts(Iterable, bool, str)
    def follow(self, waypoints, loop=False, waypoints_path_type="Linear"):
        """Tells the Pedestrian to follow the waypoints

        When a pedestrian reaches a waypoint, it will:
        1. Wait for an EGO vehicle to approach to within the trigger_distance [meters] (ignored if 0)
        2. Wait the idle time (ignored if 0)
        3. Walk to the next waypoint (if any)

        Parameters
        ----------
        waypoints : list of WalkWaypoints
        WalkWaypoint : Class (position, idle, trigger_distance, speed, acceleration)

            position : lgsvl.Vector()
            Unity coordinates of waypoint

            idle : float
            time for the pedestrian to wait at the waypoint

            trigger_distance : float
            how close an EGO must approach for the pedestrian to continue

            speed : float
            how fast the pedestrian should drive to the waypoint (default value 1)

            acceleration : float
            how fast the pedestrian will increase the speed

        loop : bool
        whether the pedestrian should loop through the waypoints after reaching the final one
        """
        self.remote.command(
            "pedestrian/follow_waypoints",
            {
                "uid": self.uid,
                "waypoints": [
                    {
                        "position": wp.position.to_json(),
                        "idle": wp.idle,
                        "trigger_distance": wp.trigger_distance,
                        "speed": wp.speed,
                        "acceleration": wp.acceleration,
                        "trigger": (
                            None if wp.trigger is None else wp.trigger.to_json()
                        ),
                    }
                    for wp in waypoints
                ],
                "waypoints_path_type": waypoints_path_type,
                "loop": loop,
            },
        )

    @accepts(float)
    def set_speed(self, speed):
        self.remote.command("pedestrian/set_speed", {"uid": self.uid, "speed": speed})

    @accepts(Callable)
    def on_waypoint_reached(self, fn):
        self.remote.command("agent/on_waypoint_reached", {"uid": self.uid})
        self.simulator._add_callback(self, "waypoint_reached", fn)
