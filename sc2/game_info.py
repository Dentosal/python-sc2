from copy import deepcopy
import itertools

from .position import Point2, Size, Rect
from .pixel_map import PixelMap
from .player import Player

class Ramp(object):
    def __init__(self, points, game_info):
        self._points = set(points) # not translated
        self.__game_info = game_info

    @property
    def _height_map(self):
        return self.__game_info.terrain_height

    @property
    def _placement_grid(self):
        return self.__game_info.placement_grid

    @property
    def size(self):
        return len(self._points)

    def height_at(self, p):
        return self._height_map[p]

    @property
    def points(self):
        return {
            Point2((p[0], self._height_map.height - p[1]))
            for p in self._points
        }

    @property
    def upper(self):
        max_height = max([self.height_at(p) for p in self._points])
        return {
            Point2((p[0], self._height_map.height - p[1]))
            for p in self._points
            if self.height_at(p) == max_height
        }

    @property
    def lower(self):
        min_height = max([self.height_at(p) for p in self._points])
        return {
            Point2((p[0], self._height_map.height - p[1]))
            for p in self._points
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

        return p2 if p1 in self._points else p1

    @property
    def _nearby(self):
        minx = min(p.x for p in self.upper)
        miny = min(p.y for p in self.upper)
        maxx = max(p.x for p in self.upper)
        maxy = max(p.y for p in self.upper)

        rect_x = max(minx - 2, 0)
        rect_y = max(miny - 2, 0)
        rect_w = min(maxx - rect_x + 3, self.__game_info.terrain_height.width)
        rect_h = min(maxy - rect_y + 3, self.__game_info.terrain_height.height)

        for y in range(rect_h):
            for x in range(rect_w):
                yield Point2((rect_x + x, rect_y + y))

    @property
    def _top_edge_12(self):
        """Top edge, with tiles on distances 1 and 2."""

        def placement_allowed(p):
            return self._placement_grid.is_set(
                Point2((p.x, self._height_map.height - p.y))
            )

        edge_p1s = set()
        edge_p2s = set()
        for up in self.upper:
            for p1 in up.neighbors8:
                if placement_allowed(p1):
                    edge_p1s.add(p1)

                for p2 in p1.neighbors4:
                    if placement_allowed(p2):
                        edge_p2s.add(p2)

        edge_p2s -= edge_p1s
        return (edge_p1s, edge_p2s)

    @property
    def top_wall_depos(self):
        """Supply depo positions (top-left) to wall the top of this ramp."""
        cover_p1s, cover_p2s = self._top_edge_12

        depos = set()
        depo_cover_p1s = cover_p1s.copy()

        # Select end of cover line for cursor
        cursor = min(cover_p1s, key=lambda p: sum([n in cover_p1s for n in p.neighbors4]))

        while depo_cover_p1s:
            depo = [cursor]

            # Follow the edge/cover for the next tile
            for p in cursor.neighbors8:
                if p in depo_cover_p1s:
                    depo.append(p)

            # Update cursor
            for d in depo[1:]:
                for p in d.neighbors4:
                    if p in cover_p1s and p not in depo:
                        cursor = p

            assert 2 <= len(depo) <= 3

            # Select the one with most neighbors, i.e. the inner one
            depo = sorted(depo, key=lambda p: sum([n in cover_p1s for n in p.neighbors4]), reverse=True)

            # Find outer spots to make 2x2 squares
            for d in depo.copy():
                for p in d.neighbors4:
                    if p in cover_p2s and p not in depo:
                        depo.append(p)
                        if len(depo) == 4:
                            break
                if len(depo) == 4:
                    break

            assert len(depo) == 4

            yield  frozenset(depo) # Point2((min(depo).x, min(depo).y))
            depo_cover_p1s -= frozenset(depo)




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
        self.player_start_location = None # Filled later by BotAI._prepare_first_step

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
        return [Ramp(g, self) for g in gs if len(g) > 1]
