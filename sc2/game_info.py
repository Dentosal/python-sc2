from copy import deepcopy
import itertools

from .position import Point2, Size, Rect
from .pixel_map import PixelMap
from .player import Player

class Ramp(object):
    def __init__(self, points, height_map):
        self.points = set(points)
        self.__height_map = height_map

    @property
    def size(self):
        return len(self.points)

    def height_at(self, p):
        return self.__height_map[p]

    @property
    def upper(self):
        max_height = max([self.height_at(p) for p in self.points])
        return {
            Point2((p[0], self.__height_map.height - p[1]))
            for p in self.points
            if self.height_at(p) == max_height
        }

    @property
    def lower(self):
        min_height = max([self.height_at(p) for p in self.points])
        return {
            Point2((p[0], self.__height_map.height - p[1]))
            for p in self.points
            if self.height_at(p) == min_height
        }

    @property
    def top_center(self):
        upper = self.upper

        minx = min(p.x for p in upper)
        miny = min(p.y for p in upper)
        maxx = max(p.x for p in upper)
        maxy = max(p.y for p in upper)

        p1 = Point2((minx, miny))
        p2 = Point2((maxx, maxy))

        return p2 if p1 in self.points else p1

class GameInfo(object):
    def __init__(self, proto):
        self.players = [Player.from_proto(p) for p in proto.player_info]
        self.map_size = Size.from_proto(proto.start_raw.map_size)
        self.pathing_grid = PixelMap(proto.start_raw.pathing_grid)
        self.terrain_height = PixelMap(proto.start_raw.terrain_height)
        self.placement_grid = PixelMap(proto.start_raw.placement_grid)
        self.playable_area = Rect.from_proto(proto.start_raw.playable_area)
        self.map_ramps =  self._find_ramps()
        self.player_races = {p.player_id: p.race_actual or p.race_requested for p in proto.player_info}
        self.start_locations = [Point2.from_proto(sl) for sl in proto.start_raw.start_locations]

    @property
    def map_center(self):
        return self.playable_area.center

    def _find_ramps(self):
        """Calculate (self.pathing_grid - self.placement_grid) (for sets) and then find ramps by comparing heights."""
        values = [
            self.terrain_height[(x, y)]
            for x in range(self.pathing_grid.width)
            for y in range(self.pathing_grid.height)
            if self.pathing_grid[(x, y)] == 0 and self.placement_grid[(x, y)] == 0
        ]

        limits = min(values), max(values)
        result = deepcopy(self.pathing_grid)

        for x in range(self.pathing_grid.width):
            for y in range(self.pathing_grid.height):
                old = self.pathing_grid[(x, y)]
                new = self.placement_grid[(x, y)]

                if old == 0 and new == 0:
                    result[(x, y)] = bytearray([self.terrain_height[(x, y)]])
                else:
                    result[(x, y)] = b"\x00"

        gs = result.flood_fill_all(lambda value: value > 0)
        return [Ramp(g, self.terrain_height) for g in gs if len(g) > 1]
