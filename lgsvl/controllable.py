#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from .geometry import Transform
from .utils import accepts, ObjectState


class Controllable:
    def __init__(self, remote, j):
        self.remote = remote
        self.uid = j["uid"]
        self.type = j["type"]
        self.transform = Transform.from_json(j)
        self.valid_actions = j["valid_actions"]
        self.default_control_policy = j["default_control_policy"]

    @property
    def object_state(self):
        j = self.remote.command("controllable/object_state/get", {"uid": self.uid})
        return ObjectState.from_json(j)

    @object_state.setter
    @accepts(ObjectState)
    def object_state(self, object_state):
        self.remote.command("controllable/object_state/set", {
            "uid": self.uid,
            "state": object_state.to_json()
        })

    @property
    def current_state(self):
        j = self.remote.command("controllable/current_state/get", {"uid": self.uid})
        return j["state"]

    @property
    def control_policy(self):
        j = self.remote.command("controllable/control_policy/get", {"uid": self.uid})
        return j["control_policy"]

    @accepts((str, list))
    def control(self, control_policy):
        self.remote.command("controllable/control_policy/set", {
            "uid": self.uid,
            "control_policy": control_policy,
        })

    def __eq__(self, other):
        return self.uid == other.uid

    def __hash__(self):
        return hash(self.uid)

    def __repr__(self):
        return str({
            "type": str(self.type),
            "transform": str(self.transform),
            "valid_actions": str(self.valid_actions),
            "default_control_policy": str(self.default_control_policy),
        })
