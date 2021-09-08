#
# Copyright (c) 2019-2020 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from math import sqrt


class Vector:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def from_json(j):
        return Vector(j["x"], j["y"], j["z"])

    def to_json(self):
        return {"x": self.x, "y": self.y, "z": self.z}

    def __repr__(self):
        return "Vector({}, {}, {})".format(self.x, self.y, self.z)

    def __add__(self, v):
        if isinstance(v, Vector):
            return Vector(self.x + v.x, self.y + v.y, self.z + v.z)
        elif isinstance(v, (int, float)):
            return Vector(self.x + v, self.y + v, self.z + v)
        else:
            raise TypeError("Vector addition only allowed between Vectors and numbers")

    def __sub__(self, v):
        if isinstance(v, Vector):
            return Vector(self.x - v.x, self.y - v.y, self.z - v.z)
        elif isinstance(v, (int, float)):
            return Vector(self.x - v, self.y - v, self.z - v)
        else:
            raise TypeError("Vector subtraction only allowed between Vectors and numbers")

    def __mul__(self, v):
        if isinstance(v, Vector):
            return Vector(self.x * v.x, self.y * v.y, self.z * v.z)
        elif isinstance(v, (int, float)):
            return Vector(self.x * v, self.y * v, self.z * v)
        else:
            raise TypeError("Vector multiplication only allowed between Vectors and numbers")

    def __rmul__(self, v):
        return self * v

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def magnitude(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)


class BoundingBox:
    def __init__(self, min, max):
        self.min = min
        self.max = max

    @staticmethod
    def from_json(j):
        return BoundingBox(Vector.from_json(j["min"]), Vector.from_json(j["max"]))

    def to_json(self):
        return {"min": self.min.to_json(), "max": self.max.to_json()}

    def __repr__(self):
        return "BoundingBox({}, {})".format(self.min, self.max)

    @property
    def center(self):
        return Vector(
            (self.max.x + self.min.x) * 0.5,
            (self.max.y + self.min.y) * 0.5,
            (self.max.z + self.min.z) * 0.5,
        )

    @property
    def size(self):
        return Vector(
            self.max.x - self.min.x,
            self.max.y - self.min.y,
            self.max.z - self.min.z,
        )


class Transform:
    def __init__(self, position=None, rotation=None):
        if position is None: position = Vector()
        if rotation is None: rotation = Vector()
        self.position = position
        self.rotation = rotation

    @staticmethod
    def from_json(j):
        return Transform(Vector.from_json(j["position"]), Vector.from_json(j["rotation"]))

    def to_json(self):
        return {"position": self.position.to_json(), "rotation": self.rotation.to_json()}

    def __repr__(self):
        return "Transform(position={}, rotation={})".format(self.position, self.rotation)


class Spawn:
    def __init__(self, transform=None, destinations=None):
        if transform is None: transform = Transform()
        if destinations is None: destinations = []
        self.position = transform.position
        self.rotation = transform.rotation
        self.destinations = destinations

    @staticmethod
    def from_json(j):
        spawn_point = Transform.from_json(j)
        destinations = []
        if "destinations" in j:
            for d in j["destinations"]:
                destinations.append(Transform.from_json(d))

        return Spawn(spawn_point, destinations)

    def to_json(self):
        return {"position": self.position.to_json(), "rotation": self.rotation.to_json()}

    def __repr__(self):
        return "Spawn(position={}, rotation={}, destinations={})".format(
            self.position, self.rotation, self.destinations
        )


class Quaternion:
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    @staticmethod
    def from_json(j):
        return Quaternion(j["x"], j["y"], j["z"], j["w"])

    def to_json(self):
        return {"x": self.x, "y": self.y, "z": self.z, "w": self.w}

    def __repr__(self):
        return "Quaternion({}, {}, {}, {})".format(self.x, self.y, self.z, self.w)
