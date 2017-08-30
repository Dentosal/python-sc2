from .position import Point2, Size, Rect
from .pixel_map import PixelMap
from .player import Player

class GameInfo(object):
    def __init__(self, proto):
        self.players = [Player.from_proto(p) for p in proto.player_info]
        self.map_size = Size.from_proto(proto.start_raw.map_size)
        self.pathing_grid = PixelMap(proto.start_raw.pathing_grid)
        self.terrain_height = PixelMap(proto.start_raw.terrain_height)
        self.placement_grid = PixelMap(proto.start_raw.placement_grid)
        self.playable_area = Rect.from_proto(proto.start_raw.playable_area)
        self.player_races = {p.player_id: p.race_actual or p.race_requested for p in proto.player_info}
        self.start_locations = [Point2.from_proto(sl) for sl in proto.start_raw.start_locations]

    @property
    def map_center(self):
        return self.playable_area.center
