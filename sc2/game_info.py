from copy import deepcopy

from .position import Point2, Size, Rect
from .pixel_map import PixelMap
from .player import Player

def _pxmap_sub_scale(map1, map2, map3):
    """ (map1 - map2) * map3 """

    assert map1.width == map2.width and map1.height == map2.height

    values = [map3[(x, y)] for x in range(map1.width) for y in range(map1.height) if map1[(x, y)] == 0 and map2[(x, y)] == 0]
    limits = min(values), max(values)

    result = deepcopy(map1)

    for x in range(map1.width):
        for y in range(map1.height):
            old = map1[(x, y)]
            new = map2[(x, y)]

            if old == 0 and new == 0:
                scaled = int((map3[(x, y)] - limits[0]) * 255) // (limits[1] - limits[0])
                result[(x, y)] = bytearray([scaled])
            else:
                result[(x, y)] = b"\x00"

    return result

class GameInfo(object):
    def __init__(self, proto):
        self.players = [Player.from_proto(p) for p in proto.player_info]
        self.map_size = Size.from_proto(proto.start_raw.map_size)
        self.pathing_grid = PixelMap(proto.start_raw.pathing_grid)
        self.terrain_height = PixelMap(proto.start_raw.terrain_height)
        self.placement_grid = PixelMap(proto.start_raw.placement_grid)
        self.playable_area = Rect.from_proto(proto.start_raw.playable_area)
        self.map_ramps = _pxmap_sub_scale(self.pathing_grid, self.placement_grid, self.terrain_height)
        self.player_races = {p.player_id: p.race_actual or p.race_requested for p in proto.player_info}
        self.start_locations = [Point2.from_proto(sl) for sl in proto.start_raw.start_locations]

    @property
    def map_center(self):
        return self.playable_area.center
