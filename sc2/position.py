import itertools
import math
import random
from typing import Any, Dict, List, Optional, Set, Tuple, Union  # for mypy type checking

FLOAT_DIGITS = 8
EPSILON = 10 ** (-FLOAT_DIGITS)


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

    def distance_to(self, p: Union["Unit", "Point2", "Point3"]) -> Union[int, float]:
        p = p.position
        assert isinstance(p, Pointlike)
        if self == p:
            return 0
        return (sum(self.__class__((b - a) ** 2 for a, b in itertools.zip_longest(self, p, fillvalue=0)))) ** 0.5

    def distance_to_point2(self, p2: "Point2") -> Union[int, float]:
        """ Same as the function above, but should be 3-4 times faster because of the dropped asserts and conversions and because it doesnt use a loop (itertools or zip). """
        return ((self[0] - p2[0]) ** 2 + (self[1] - p2[1]) ** 2) ** 0.5

    def _distance_squared(self, p2: "Point2") -> Union[int, float]:
        """ Function used to not take the square root as the distances will stay proportionally the same. This is to speed up the sorting process. """
        return (self[0] - p2[0]) ** 2 + (self[1] - p2[1]) ** 2

    def sort_by_distance(self, ps: Union["Units", List["Point2"]]) -> List["Point2"]:
        """ This returns the target points sorted as list. You should not pass a set or dict since those are not sortable.
        If you want to sort your units towards a point, use 'units.sorted_by_distance_to(point)' instead. """
        if len(ps) == 1:
            return ps[0]
        # if ps and all(isinstance(p, Point2) for p in ps):
        #     return sorted(ps, key=lambda p: self._distance_squared(p))
        return sorted(ps, key=lambda p: self._distance_squared(p.position))

    def closest(self, ps: Union["Units", List["Point2"], Set["Point2"]]) -> Union["Unit", "Point2"]:
        """ This function assumes the 2d distance is meant """
        assert ps
        if len(ps) == 1:
            return ps[0]
        closest_distance_squared = math.inf
        for p2 in ps:
            p2pos = p2
            if not isinstance(p2pos, Point2):
                p2pos = p2.position
            distance = (self[0] - p2pos[0]) ** 2 + (self[1] - p2pos[1]) ** 2
            if distance < closest_distance_squared:
                closest_distance_squared = distance
                closest_element = p2
        return closest_element

    def distance_to_closest(self, ps: Union["Units", List["Point2"], Set["Point2"]]) -> Union[int, float]:
        """ This function assumes the 2d distance is meant """
        assert ps
        closest_distance_squared = math.inf
        for p2 in ps:
            if not isinstance(p2, Point2):
                p2 = p2.position
            distance = (self[0] - p2[0]) ** 2 + (self[1] - p2[1]) ** 2
            if distance < closest_distance_squared:
                closest_distance_squared = distance
        return closest_distance_squared ** 0.5

    def furthest(self, ps: Union["Units", List["Point2"], Set["Point2"]]) -> Union["Unit", "Pointlike"]:
        """ This function assumes the 2d distance is meant """
        assert ps
        if len(ps) == 1:
            return ps[0]
        furthest_distance_squared = -math.inf
        for p2 in ps:
            p2pos = p2
            if not isinstance(p2pos, Point2):
                p2pos = p2.position
            distance = (self[0] - p2pos[0]) ** 2 + (self[1] - p2pos[1]) ** 2
            if furthest_distance_squared < distance:
                furthest_distance_squared = distance
                furthest_element = p2
        return furthest_element

    def distance_to_furthest(self, ps: Union["Units", List["Point2"], Set["Point2"]]) -> Union[int, float]:
        """ This function assumes the 2d distance is meant """
        assert ps
        furthest_distance_squared = -math.inf
        for p2 in ps:
            if not isinstance(p2, Point2):
                p2 = p2.position
            distance = (self[0] - p2[0]) ** 2 + (self[1] - p2[1]) ** 2
            if furthest_distance_squared < distance:
                furthest_distance_squared = distance
        return furthest_distance_squared ** 0.5

    def offset(self, p) -> "Pointlike":
        return self.__class__(a + b for a, b in itertools.zip_longest(self, p[: len(self)], fillvalue=0))

    def unit_axes_towards(self, p):
        return self.__class__(_sign(b - a) for a, b in itertools.zip_longest(self, p[: len(self)], fillvalue=0))

    def towards(
        self, p: Union["Unit", "Pointlike"], distance: Union[int, float] = 1, limit: bool = False
    ) -> "Pointlike":
        p = p.position
        # assert self != p, f"self is {self}, p is {p}"
        # TODO test and fix this if statement
        if self == p:
            return self
        # end of test
        d = self.distance_to(p)
        if limit:
            distance = min(d, distance)
        return self.__class__(
            a + (b - a) / d * distance for a, b in itertools.zip_longest(self, p[: len(self)], fillvalue=0)
        )

    def __eq__(self, other):
        if not isinstance(other, tuple):
            return False
        return all(abs(a - b) < EPSILON for a, b in itertools.zip_longest(self, other, fillvalue=0))

    def __hash__(self):
        return hash(tuple(int(c * FLOAT_DIGITS) for c in self))


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

    def distance2_to(self, other: "Point2"):
        """Squared distance to a point."""
        assert isinstance(other, Point2)
        return (self[0] - other[0]) ** 2 + (self[1] - other[1]) ** 2

    def random_on_distance(self, distance):
        if isinstance(distance, (tuple, list)):  # interval
            distance = distance[0] + random.random() * (distance[1] - distance[0])

        assert distance > 0
        angle = random.random() * 2 * math.pi

        dx, dy = math.cos(angle), math.sin(angle)
        return Point2((self.x + dx * distance, self.y + dy * distance))

    def towards_with_random_angle(
        self,
        p: Union["Point2", "Point3"],
        distance: Union[int, float] = 1,
        max_difference: Union[int, float] = (math.pi / 4),
    ) -> "Point2":
        tx, ty = self.to2.towards(p.to2, 1)
        angle = math.atan2(ty - self.y, tx - self.x)
        angle = (angle - max_difference) + max_difference * 2 * random.random()
        return Point2((self.x + math.cos(angle) * distance, self.y + math.sin(angle) * distance))

    def circle_intersection(self, p: "Point2", r: Union[int, float]) -> Set["Point2"]:
        """ self is point1, p is point2, r is the radius for circles originating in both points
        Used in ramp finding """
        assert self != p
        distanceBetweenPoints = self.distance_to(p)
        assert r > distanceBetweenPoints / 2
        # remaining distance from center towards the intersection, using pythagoras
        remainingDistanceFromCenter = (r ** 2 - (distanceBetweenPoints / 2) ** 2) ** 0.5
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

    def negative_offset(self, other: "Point2") -> "Point2":
        return self.__class__((self.x - other.x, self.y - other.y))

    def __add__(self, other: "Point2") -> "Point2":
        return self.offset(other)

    def __sub__(self, other: "Point2") -> "Point2":
        return self.negative_offset(other)

    def __neg__(self) -> "Point2":
        return self.__class__(-a for a in self)

    def __abs__(self) -> Union[int, float]:
        return math.hypot(self.x, self.y)

    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0

    def __mul__(self, other: Union[int, float, "Point2"]) -> "Point2":
        if isinstance(other, self.__class__):
            return self.__class__((self.x * other.x, self.y * other.y))
        return self.__class__((self.x * other, self.y * other))

    def __rmul__(self, other: Union[int, float, "Point2"]) -> "Point2":
        return self.__mul__(other)

    def __truediv__(self, other: Union[int, float, "Point2"]) -> "Point2":
        if isinstance(other, self.__class__):
            return self.__class__((self.x / other.x, self.y / other.y))
        return self.__class__((self.x / other, self.y / other))

    def is_same_as(self, other: "Point2", dist=0.1) -> bool:
        return self._distance_squared(other) <= dist ** 2

    def direction_vector(self, other: "Point2") -> "Point2":
        """ Converts a vector to a direction that can face vertically, horizontally or diagonal or be zero, e.g. (0, 0), (1, -1), (1, 0) """
        return self.__class__((_sign(other.x - self.x), _sign(other.y - self.y)))

    def manhattan_distance(self, other: "Point2") -> Union[int, float]:
        return abs(other.x - self.x) + abs(other.y - self.y)

    @staticmethod
    def center(a: Union[Set["Point2"], List["Point2"]]) -> "Point2":
        """ Returns the central point for points in list """
        s = Point2((0, 0))
        for p in a:
            s += p
        return s / len(a)


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
    def width(self) -> Union[int, float]:
        return self[0]

    @property
    def height(self) -> Union[int, float]:
        return self[1]


class Rect(tuple):
    @classmethod
    def from_proto(cls, data):
        assert data.p0.x < data.p1.x and data.p0.y < data.p1.y
        return cls((data.p0.x, data.p0.y, data.p1.x - data.p0.x, data.p1.y - data.p0.y))

    @property
    def x(self) -> Union[int, float]:
        return self[0]

    @property
    def y(self) -> Union[int, float]:
        return self[1]

    @property
    def width(self) -> Union[int, float]:
        return self[2]

    @property
    def height(self) -> Union[int, float]:
        return self[3]

    @property
    def size(self) -> Size:
        return Size(self[2], self[3])

    @property
    def center(self) -> Point2:
        return Point2((self.x + self.width / 2, self.y + self.height / 2))

    def offset(self, p):
        return self.__class__((self[0] + p[0], self[1] + p[1], self[2], self[3]))
