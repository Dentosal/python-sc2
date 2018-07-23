from math import sqrt, pi, sin, cos, atan2
import random
import itertools
from typing import List, Dict, Set, Tuple, Any, Optional, Union # for mypy type checking

FLOAT_DIGITS = 8
EPSILON = 10**(-FLOAT_DIGITS)

def _sign(num):
    if num == 0:
        return 0
    return 1 if num > 0 else -1

class Pointlike(tuple):
    @property
    def rounded(self) -> "Pointlike":
        return self.__class__(round(q) for q in self)

    @property
    def position(self) -> "Pointlike":
        return self

    def distance_to(self, p: Union["Unit", "Pointlike"]) -> Union[int, float]:
        p = p.position
        assert isinstance(p, Pointlike)
        if self == p:
            return 0
        return sqrt(sum(self.__class__((b-a)**2 for a, b in itertools.zip_longest(self, p, fillvalue=0))))

    def sort_by_distance(self, ps):
        return sorted(ps, key=lambda p: self.distance_to(p))

    def closest(self, ps) -> Union["Unit", "Pointlike"]:
        assert len(ps) > 0
        return min(ps, key=lambda p: self.distance_to(p))

    def distance_to_closest(self, ps) -> Union[int, float]:
        assert len(ps) > 0
        return min(ps, key=lambda p: self.distance_to(p)).distance_to(self)

    def furthest(self, ps) -> Union["Unit", "Pointlike"]:
        assert len(ps) > 0
        return max(ps, key=lambda p: self.distance_to(p))

    def distance_to_furthest(self, ps) -> Union[int, float]:
        assert len(ps) > 0
        return max(ps, key=lambda p: self.distance_to(p)).distance_to(self)

    def offset(self, p) -> "Pointlike":
        return self.__class__(a+b for a, b in itertools.zip_longest(self, p[:len(self)], fillvalue=0))

    def unit_axes_towards(self, p):
        return self.__class__(_sign(b - a) for a, b in itertools.zip_longest(self, p[:len(self)], fillvalue=0))

    def towards(self, p: Union["Unit", "Pointlike"], distance: Union[int, float]=1, limit: bool=False) -> "Pointlike":
        assert self != p
        d = self.distance_to(p)
        if limit:
            distance = min(d, distance)
        return self.__class__(a + (b - a) / d * distance for a, b in itertools.zip_longest(self, p[:len(self)], fillvalue=0))

    def __eq__(self, other):
        if not isinstance(other, tuple):
            return False
        return all(abs(a - b) < EPSILON for a, b in itertools.zip_longest(self, other, fillvalue=0))

    def __hash__(self):
        return hash(tuple(int(c * FLOAT_DIGITS)  for c in self))


class Point2(Pointlike):
    @classmethod
    def from_proto(cls, data):
        return cls((data.x, data.y))

    @property
    def x(self) -> Union[int, float]:
        return self[0]

    @property
    def y(self) -> Union[int, float]:
        return self[1]

    @property
    def to2(self) -> "Point2":
        return Point2(self[:2])

    @property
    def to3(self) -> "Point3":
        return Point3((*self, 0))

    def random_on_distance(self, distance):
        if isinstance(distance, (tuple, list)): # interval
            distance = distance[0] + random.random() * (distance[1] - distance[0])

        assert distance > 0
        angle = random.random() * 2 * pi

        dx, dy = cos(angle), sin(angle)
        return Point2((self.x + dx * distance, self.y + dy * distance))

    def towards_with_random_angle(self, p, distance=1, max_difference=(pi/4)):
        tx, ty = self.to2.towards(p.to2, 1)
        angle = atan2(ty - self.y, tx - self.x)
        angle = (angle - max_difference) + max_difference * 2 * random.random()
        return Point2((self.x + cos(angle) * distance, self.y + sin(angle) * distance))

    def circle_intersection(self, p: "Point2", r: Union[int, float]) -> Set["Point2"]:
        """ self is point1, p is point2, r is the radius for circles originating in both points
        Used in ramp finding """
        assert self != p
        distanceBetweenPoints = self.distance_to(p)
        assert r > distanceBetweenPoints / 2
        # remaining distance from center towards the intersection, using pythagoras
        remainingDistanceFromCenter = (r**2 - (distanceBetweenPoints/2)**2)**0.5
        # center of both points
        offsetToCenter = Point2(((p.x - self.x) / 2, (p.y - self.y) / 2))
        center = self.offset(offsetToCenter)

        # stretch offset vector in the ratio of remaining distance from center to intersection
        vectorStretchFactor = remainingDistanceFromCenter / (distanceBetweenPoints / 2)
        v = offsetToCenter
        offsetToCenterStretched = Point2((v.x * vectorStretchFactor, v.y * vectorStretchFactor))

        # rotate vector by 90° and -90°
        vectorRotated1 = Point2((offsetToCenterStretched.y, -offsetToCenterStretched.x))
        vectorRotated2 = Point2((-offsetToCenterStretched.y, offsetToCenterStretched.x))
        intersect1 = center.offset(vectorRotated1)
        intersect2 = center.offset(vectorRotated2)
        return {intersect1, intersect2}

    @property
    def neighbors4(self) -> set:
        return {
            Point2((self.x - 1, self.y)),
            Point2((self.x + 1, self.y)),
            Point2((self.x, self.y - 1)),
            Point2((self.x, self.y + 1)),
        }

    @property
    def neighbors8(self) -> set:
        return self.neighbors4 | {
            Point2((self.x - 1, self.y - 1)),
            Point2((self.x - 1, self.y + 1)),
            Point2((self.x + 1, self.y - 1)),
            Point2((self.x + 1, self.y + 1)),
        }


class Point3(Point2):
    @classmethod
    def from_proto(cls, data):
        return cls((data.x, data.y, data.z))

    @property
    def z(self) -> Union[int, float]:
        return self[2]

    @property
    def to3(self) -> "Point3":
        return Point3(self)

class Size(Point2):
    @property
    def width(self):
        return self[0]

    @property
    def height(self):
        return self[1]

class Rect(tuple):
    @classmethod
    def from_proto(cls, data):
        assert data.p0.x < data.p1.x and data.p0.y < data.p1.y
        return cls((data.p0.x, data.p0.y, data.p1.x - data.p0.x, data.p1.y - data.p0.y))

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def width(self):
        return self[2]

    @property
    def height(self):
        return self[3]

    @property
    def size(self):
        return Size(self[2], self[3])

    @property
    def center(self):
        return Point2((self.x + self.width / 2, self.y + self.height / 2))

    def offset(self, p):
        return self.__class__((self[0]+p[0], self[1]+p[1], self[2], self[3]))
