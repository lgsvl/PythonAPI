#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from .remote import Remote
from .agent import Agent, AgentType, AgentState
from .sensor import GpsData
from .geometry import Vector, Transform, Spawn, Quaternion
from .utils import accepts, ObjectState
from .controllable import Controllable

from enum import Enum
from collections import namedtuple
from environs import Env
from datetime import datetime
import re

RaycastHit = namedtuple("RaycastHit", "distance point normal")

WeatherState = namedtuple("WeatherState", "rain fog wetness cloudiness damage")
WeatherState.__new__.__defaults__ = (0,) * len(WeatherState._fields)

env = Env()


class Simulator:

    class SimulatorCameraState(Enum):
        FREE = 0
        FOLLOW = 1
        CINEMATIC = 2
        DRIVER = 3

    @accepts(str, int)
    def __init__(self, address=env.str("LGSVL__SIMULATOR_HOST", "localhost"), port=env.int("LGSVL__SIMULATOR_PORT", 8181)):
        if port <= 0 or port > 65535:
            raise ValueError("port value is out of range")
        self.remote = Remote(address, port)
        self.agents = {}
        self.callbacks = {}
        self.stopped = False

    def close(self):
        self.remote.close()

    @accepts(str, int)
    def load(self, scene, seed=None):
        self.remote.command("simulator/load_scene", {"scene": scene, "seed": seed})
        self.agents.clear()
        self.callbacks.clear()

    @property
    def version(self):
        return self.remote.command("simulator/version")

    @property
    def layers(self):
        return self.remote.command("simulator/layers/get")

    @property
    def current_scene(self):
        return self.remote.command("simulator/current_scene")

    @property
    def current_scene_id(self):
        return self.remote.command("simulator/current_scene_id")

    @property
    def current_frame(self):
        return self.remote.command("simulator/current_frame")

    @property
    def current_time(self):
        return self.remote.command("simulator/current_time")

    @property
    def available_agents(self):
        return self.remote.command("simulator/available_agents")

    @property
    def available_npc_behaviours(self):
        return self.remote.command("simulator/npc/available_behaviours")

    @accepts(Transform)
    def set_sim_camera(self, transform):
        self.remote.command("simulator/camera/set", {"transform": transform.to_json()})

    @accepts(SimulatorCameraState)
    def set_sim_camera_state(self, state):
        self.remote.command("simulator/camera/state/set", {"state": state.value})

    def agents_traversed_waypoints(self, fn):
        self._add_callback(None, "agents_traversed_waypoints", fn)

    def reset(self):
        self.remote.command("simulator/reset")
        self.agents.clear()
        self.callbacks.clear()

    def stop(self):
        self.stopped = True

    @accepts((int, float), (int, float))
    def run(self, time_limit=0.0, time_scale=None):
        self._process("simulator/run", {"time_limit": time_limit, "time_scale": time_scale})

    def _add_callback(self, agent, name, fn):
        if agent not in self.callbacks:
            self.callbacks[agent] = {}
        if name not in self.callbacks[agent]:
            self.callbacks[agent][name] = set()
        self.callbacks[agent][name].add(fn)

    def _process_events(self, events):
        self.stopped = False
        for ev in events:
            if "agent" in ev:
                agent = self.agents[ev["agent"]]
                if agent in self.callbacks:
                    callbacks = self.callbacks[agent]
                    event_type = ev["type"]
                    if event_type in callbacks:
                        for fn in callbacks[event_type]:
                            if event_type == "collision":
                                fn(agent, self.agents.get(ev["other"]), Vector.from_json(ev["contact"]) if ev["contact"] is not None else None)
                            elif event_type == "waypoint_reached":
                                fn(agent, ev["index"])
                            elif event_type == "stop_line":
                                fn(agent)
                            elif event_type == "lane_change":
                                fn(agent)
                            elif event_type == "destination_reached":
                                fn(agent)
                            elif event_type == "custom":
                                fn(agent, ev["kind"], ev["context"])
                            if self.stopped:
                                return
            elif None in self.callbacks:
                callbacks = self.callbacks[None]
                event_type = ev["type"]
                if event_type in callbacks:
                    for fn in callbacks[event_type]:
                        if event_type == "agents_traversed_waypoints":
                            fn()

    def _process(self, cmd, args):
        j = self.remote.command(cmd, args)
        while True:
            if j is None:
                return
            if "events" in j:
                self._process_events(j["events"])
                if self.stopped:
                    break
            j = self.remote.command("simulator/continue")

    @accepts(str, AgentType, (AgentState, type(None)), (Vector, type(None)))
    def add_agent(self, name, agent_type, state=None, color=None):
        if state is None: state = AgentState()
        if color is None: color = Vector(-1, -1, -1)
        args = {"name": name, "type": agent_type.value, "state": state.to_json(), "color": color.to_json()}
        uid = self.remote.command("simulator/add_agent", args)
        agent = Agent.create(self, uid, agent_type)
        agent.name = name
        self.agents[uid] = agent
        return agent

    @accepts(Agent)
    def remove_agent(self, agent):
        self.remote.command("simulator/agent/remove", {"uid": agent.uid})
        del self.agents[agent.uid]
        if agent in self.callbacks:
            del self.callbacks[agent]

    @accepts(AgentType)
    def add_random_agents(self, agent_type):
        args = {"type": agent_type.value}
        self.remote.command("simulator/add_random_agents", args)

    def get_agents(self):
        return list(self.agents.values())

    @property
    def weather(self):
        j = self.remote.command("environment/weather/get")
        return WeatherState(j.get("rain", 0), j.get("fog", 0), j.get("wetness", 0), j.get("cloudiness", 0), j.get("damage", 0))

    @weather.setter
    @accepts(WeatherState)
    def weather(self, state):
        self.remote.command("environment/weather/set", {"rain": state.rain, "fog": state.fog, "wetness": state.wetness, "cloudiness": state.cloudiness, "damage": state.damage})

    @property
    def time_of_day(self):
        return self.remote.command("environment/time/get")

    @property
    def current_datetime(self):
        date_time_str = self.remote.command("simulator/datetime/get")
        date_time_arr = list(map(int, re.split('[. :]', date_time_str)))
        date_time = datetime(
            date_time_arr[2],
            date_time_arr[1],
            date_time_arr[0],
            date_time_arr[3],
            date_time_arr[4],
            date_time_arr[5]
        )
        return date_time

    @accepts((int, float), bool)
    def set_time_of_day(self, time, fixed=True):
        self.remote.command("environment/time/set", {"time": time, "fixed": fixed})

    @accepts(datetime, bool)
    def set_date_time(self, date_time, fixed=True):
        date_time = date_time.__str__()
        self.remote.command("environment/datetime/set", {"datetime": date_time, "fixed": fixed})

    def get_spawn(self):
        spawns = self.remote.command("map/spawn/get")
        return [Spawn.from_json(spawn) for spawn in spawns]

    @accepts((Transform, Spawn))
    def map_to_gps(self, transform):
        j = self.remote.command("map/to_gps", {"transform": transform.to_json()})
        return GpsData(j["latitude"], j["longitude"], j["northing"], j["easting"], j["altitude"], j["orientation"])

    def map_from_gps(self, latitude=None, longitude=None, northing=None, easting=None, altitude=None, orientation=None):
        c = []
        coord = {
            "latitude": latitude,
            "longitude": longitude,
            "northing": northing,
            "easting": easting,
            "altitude": altitude,
            "orientation": orientation
        }
        c.append(coord)
        return self.map_from_gps_batch(c)[0]

    def map_from_gps_batch(self, coords):
        # coords dictionary
        jarr = []

        for c in coords:
            j = {}
            numtype = (int, float)
            if ("latitude" in c and c["latitude"] is not None) and ("longitude" in c and c["longitude"] is not None):
                if not isinstance(c["latitude"], numtype): raise TypeError("Argument 'latitude' should have '{}' type".format(numtype))
                if not isinstance(c["longitude"], numtype): raise TypeError("Argument 'longitude' should have '{}' type".format(numtype))
                if c["latitude"] < -90 or c["latitude"] > 90: raise ValueError("Latitude is out of range")
                if c["longitude"] < -180 or c["longitude"] > 180: raise ValueError("Longitude is out of range")
                j["latitude"] = c["latitude"]
                j["longitude"] = c["longitude"]
            elif ("northing" in c and c["northing"] is not None) and ("easting" in c and c["easting"] is not None):
                if not isinstance(c["northing"], numtype): raise TypeError("Argument 'northing' should have '{}' type".format(numtype))
                if not isinstance(c["easting"], numtype): raise TypeError("Argument 'easting' should have '{}' type".format(numtype))
                if c["northing"] < 0 or c["northing"] > 10000000: raise ValueError("Northing is out of range")
                if c["easting"] < 160000 or c["easting"] > 834000: raise ValueError("Easting is out of range")
                j["northing"] = c["northing"]
                j["easting"] = c["easting"]
            else:
                raise Exception("Either latitude and longitude or northing and easting should be specified")
            if "altitude" in c and c["altitude"] is not None:
                if not isinstance(c["altitude"], numtype): raise TypeError("Argument 'altitude' should have '{}' type".format(numtype))
                j["altitude"] = c["altitude"]
            if "orientation" in c and c["orientation"] is not None:
                if not isinstance(c["orientation"], numtype): raise TypeError("Argument 'orientation' should have '{}' type".format(numtype))
                j["orientation"] = c["orientation"]
            jarr.append(j)

        jarr = self.remote.command("map/from_gps", jarr)
        transforms = []
        for j in jarr:
            transforms.append(Transform.from_json(j))
        return transforms

    @accepts(Vector)
    def map_point_on_lane(self, point):
        j = self.remote.command("map/point_on_lane", {"point": point.to_json()})
        return Transform.from_json(j)

    @accepts(Vector, Quaternion)
    def map_from_nav(self, position, orientation):
        res = self.remote.command(
            "map/from_nav",
            {
                "position": position.to_json(),
                "orientation": orientation.to_json()
            }
        )
        return Transform.from_json(res)

    @accepts(Transform, Vector)
    def set_nav_origin(self, transform, offset=Vector()):
        self.remote.command(
            "navigation/set_origin",
            {
                "transform": transform.to_json(),
                "offset": offset.to_json(),
            }
        )

    def get_nav_origin(self):
        res = self.remote.command("navigation/get_origin")
        nav_origin = None
        if res:
            nav_origin = {
                "transform": Transform.from_json(res),
                "offset": res["offset"]
            }
        return nav_origin

    @accepts(Vector, Vector, int, float)
    def raycast(self, origin, direction, layer_mask=-1, max_distance=float("inf")):
        hit = self.remote.command("simulator/raycast", [{
            "origin": origin.to_json(),
            "direction": direction.to_json(),
            "layer_mask": layer_mask,
            "max_distance": max_distance
        }])
        if hit[0] is None:
            return None
        return RaycastHit(hit[0]["distance"], Vector.from_json(hit[0]["point"]), Vector.from_json(hit[0]["normal"]))

    def raycast_batch(self, args):
        jarr = []
        for arg in args:
            jarr.append({
                "origin": arg["origin"].to_json(),
                "direction": arg["direction"].to_json(),
                "layer_mask": arg["layer_mask"],
                "max_distance": arg["max_distance"]
            })

        hits = self.remote.command("simulator/raycast", jarr)
        results = []
        for hit in hits:
            if hit is None:
                results.append(None)
            else:
                results.append(RaycastHit(hit["distance"], Vector.from_json(hit["point"]), Vector.from_json(hit["normal"])))

        return results

    @accepts(str, (ObjectState, type(None)))
    def controllable_add(self, name, object_state=None):
        if object_state is None: object_state = ObjectState()
        args = {"name": name, "state": object_state.to_json()}
        j = self.remote.command("simulator/controllable_add", args)
        controllable = Controllable(self.remote, j)
        controllable.name = name
        return controllable

    @accepts(Controllable)
    def controllable_remove(self, controllable):
        self.remote.command("simulator/controllable_remove", {"uid": controllable.uid})
        del self.controllables[controllable.uid]

    @accepts(str)
    def get_controllables(self, control_type=None):
        j = self.remote.command("controllable/get/all", {
            "type": control_type,
        })
        return [Controllable(self.remote, controllable) for controllable in j]

    @accepts(str)
    def get_controllable_by_uid(self, uid):
        j = self.remote.command("controllable/get", {
            "uid": uid,
        })
        return Controllable(self.remote, j)

    @accepts(Vector, str)
    def get_controllable(self, position, control_type=None):
        j = self.remote.command("controllable/get", {
            "position": position.to_json(),
            "type": control_type,
        })
        return Controllable(self.remote, j)
