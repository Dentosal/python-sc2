from math import sqrt, pi, sin, cos, atan2
import random
import itertools

def _sign(num):
    if num == 0:
        return 0
    return 1 if num > 0 else -1

class Pointlike(tuple):
    @property
    def rounded(self):
        return self.__class__(round(q) for q in self)

    @property
    def position(self):
        return self

    def distance_to(self, p):
        p = p.position
        assert isinstance(p, Pointlike)
        if self == p:
            return 0
        return sqrt(sum(self.__class__((b-a)**2 for a, b in itertools.zip_longest(self, p[:len(self)], fillvalue=0))))

    def sort_by_distance(self, ps):
        return sorted(ps, key=lambda p: self.distance_to(p))

    def closest(self, ps):
        return min(ps, key=lambda p: self.distance_to(p))

    def offset(self, p):
        return self.__class__(a+b for a, b in itertools.zip_longest(self, p[:len(self)], fillvalue=0))

    def unit_axes_towards(self, p):
        return self.__class__(_sign(b - a) for a, b in itertools.zip_longest(self, p[:len(self)], fillvalue=0))

    def towards(self, p, distance=1, limit=False):
        d = self.distance_to(p)
        if limit:
            distance = min(d, distance)
        return self.__class__(a + (b - a) / d * distance for a, b in itertools.zip_longest(self, p[:len(self)], fillvalue=0))


class Point2(Pointlike):
    @classmethod
    def from_proto(cls, data):
        return cls((data.x, data.y))

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def to2(self):
        return Point2(self[:2])

    @property
    def to3(self):
        return Point3((*self, 0))

    def random_on_distance(self, distance, angle=None):
        if isinstance(distance, tuple):
            distance = distance[0] + random.random() * (distance[1] - distance[0])

        assert distance > 0

        if angle is None:
            angle = random.random() * 2 * pi

        dx, dy = cos(angle), sin(angle)
        return Point2((self.x + dx * distance, self.y + dy * distance))

    def towards_random_angle(self, p, max_difference=(pi/4), distance=1):
        dx, dy = self.to2.towards(p.to2, 1)
        angle = atan2(dy, dx)
        angle = (angle - max_difference) + max_difference * 2 * random.random()
        return self.random_on_distance(distance, angle)


class Point3(Point2):
    @classmethod
    def from_proto(cls, data):
        return cls((data.x, data.y, data.z))

    @property
    def z(self):
        return self[2]

    @property
    def to3(self):
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
