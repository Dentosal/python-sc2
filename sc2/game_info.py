from typing import Tuple, Set, FrozenSet, Sequence, Generator

from copy import deepcopy
import itertools

from .position import Point2, Size, Rect
from .pixel_map import PixelMap
from .player import Player
from typing import List, Dict, Set, Tuple, Any, Optional, Union # mypy type checking


class Ramp:
    def __init__(self, points: Set[Point2], game_info: "GameInfo"):
        self._points: Set[Point2] = set(points)
        self.__game_info = game_info
        # tested by printing actual building locations vs calculated depot positions
        self.x_offset = 0.5 # might be errors with the pixelmap?
        self.y_offset = -0.5

    @property
    def _height_map(self):
        return self.__game_info.terrain_height

    @property
    def _placement_grid(self):
        return self.__game_info.placement_grid

    @property
    def size(self) -> int:
        return len(self._points)

    def height_at(self, p: Point2) -> int:
        return self._height_map[p]

    @property
    def points(self) -> Set[Point2]:
        return self._points.copy()

    @property
    def upper(self) -> Set[Point2]:
        max_height = max([self.height_at(p) for p in self._points])
        return {
            p
            for p in self._points
            if self.height_at(p) == max_height
        }

    @property
    def top_center(self) -> Point2:
        pos = Point2((sum([p.x for p in self.upper]) / len(self.upper), \
            sum([p.y for p in self.upper]) / len(self.upper)))
        return pos

    @property
    def lower(self) -> Set[Point2]:
        min_height = min([self.height_at(p) for p in self._points])
        return {
            p
            for p in self._points
            if self.height_at(p) == min_height
        }

    @property
    def barracks_in_middle(self) -> Point2:
        """ Barracks position in the middle of the 2 depots """
        if len(self.upper) == 2:
            points = self.upper
            p1 = points.pop().offset((self.x_offset, self.y_offset)) # still an error with pixelmap?
            p2 = points.pop().offset((self.x_offset, self.y_offset))
            # offset from top point to barracks center is (2, 1)
            intersects = p1.circle_intersection(p2, (2**2 + 1**2)**0.5)
            # intersects = p1.circle_intersection(p2, (2**2 + 1**2)**0.5)
            anyLowerPoint = next(iter(self.lower))
            return max(intersects, key=lambda p: p.distance_to(anyLowerPoint))
        raise Exception('Not implemented. Trying to access a ramp that has a wrong amount of upper points.')

    @property
    def depot_in_middle(self) -> Point2:
        """ Depot in the middle of the 3 depots """
        if len(self.upper) == 2:
            points = self.upper
            p1 = points.pop().offset((self.x_offset, self.y_offset)) # still an error with pixelmap?
            p2 = points.pop().offset((self.x_offset, self.y_offset))
            d = p1.distance_to(p2)
            # offset from top point to depot center is (1.5, 0.5)
            intersects = p1.circle_intersection(p2, (1.5**2 + 0.5**2)**0.5)
            anyLowerPoint = next(iter(self.lower))
            return max(intersects, key=lambda p: p.distance_to(anyLowerPoint))
        raise Exception('Not implemented. Trying to access a ramp that has a wrong amount of upper points.')

    @property
    def corner_depots(self) -> Set[Point2]:
        """ Finds the 2 depot positions on the outside """
        if len(self.upper) == 2:
            points = self.upper
            p1 = points.pop().offset((self.x_offset, self.y_offset)) # still an error with pixelmap?
            p2 = points.pop().offset((self.x_offset, self.y_offset))
            center = p1.towards(p2, p1.distance_to(p2) / 2)
            depotPosition = self.depot_in_middle
            # offset from middle depot to corner depots is (2, 1)
            intersects = center.circle_intersection(depotPosition, (2**2 + 1**2)**0.5)
            return intersects
        raise Exception('Not implemented. Trying to access a ramp that has a wrong amount of upper points.')

    @property
    def barracks_can_fit_addon(self) -> bool:
        """ Test if a barracks can fit an addon at natural ramp """
        # https://i.imgur.com/4b2cXHZ.png
        if len(self.upper) == 2:
            return self.barracks_in_middle.x + 1 > max(self.corner_depots, key=lambda depot: depot.x).x
        raise Exception('Not implemented. Trying to access a ramp that has a wrong amount of upper points.')

    @property
    def barracks_correct_placement(self) -> Point2:
        """ Corrected placement so that an addon can fit """
        if len(self.upper) == 2:
            if self.barracks_can_fit_addon:
                return self.barracks_in_middle
            else:
                return self.barracks_in_middle.offset((-2, 0))
        raise Exception('Not implemented. Trying to access a ramp that has a wrong amount of upper points.')


class GameInfo(object):
    def __init__(self, proto):
        # TODO: this might require an update during the game because placement grid and playable grid are greyed out on minerals, start locations and ramps (debris)
        self._proto = proto       
        self.players = [Player.from_proto(p) for p in proto.player_info]
        self.map_size = Size.from_proto(proto.start_raw.map_size)
        self.pathing_grid: PixelMap = PixelMap(proto.start_raw.pathing_grid)
        self.terrain_height: PixelMap = PixelMap(proto.start_raw.terrain_height)
        self.placement_grid: PixelMap = PixelMap(proto.start_raw.placement_grid)
        self.playable_area = Rect.from_proto(proto.start_raw.playable_area)
        self.map_ramps: List[Ramp] = self._find_ramps()
        self.player_races: Dict[int, "Race"] = {p.player_id: p.race_actual or p.race_requested for p in proto.player_info}
        self.start_locations: List[Point2] = [Point2.from_proto(sl) for sl in proto.start_raw.start_locations]
        self.player_start_location: Point2 = None # Filled later by BotAI._prepare_first_step

    @property
    def map_center(self):
        return self.playable_area.center

    def _find_ramps(self) -> List[Ramp]:
        """Calculate (self.pathing_grid - self.placement_grid) (for sets) and then find ramps by comparing heights."""
        rampDict = {
            Point2((x, y)): self.pathing_grid[(x, y)] == 0 and self.placement_grid[(x, y)] == 0
            for x in range(self.pathing_grid.width)
            for y in range(self.pathing_grid.height)
            # if self.pathing_grid[(x, y)] == 0 and self.placement_grid[(x, y)] == 0
        }

        rampPoints = {p for p in rampDict if rampDict[p]} # filter only points part of ramp
        rampGroups = self._find_groups(rampPoints)
        return [Ramp(group, self) for group in rampGroups]


    def _find_groups(self, points: Set[Point2], minimum_points_per_group: int=8, max_distance_between_points: int=2) -> List[Set[Point2]]:
        """ From a set/list of points, this function will try to group points """
        foundGroups = []
        currentGroup = set()
        pointsPool = set(points)

        while pointsPool or currentGroup:
            if len(currentGroup) == 0:
                randomPoint = pointsPool.pop()
                currentGroup.add(randomPoint)

            sizeChanged = False
            for p1 in set(currentGroup): # create copy
                for p2 in set(pointsPool): # create copy as we change set size during iteration
                    if abs(p1.x - p2.x) + abs(p1.y - p2.y) <= max_distance_between_points:
                        sizeChanged = True
                        currentGroup.add(p2)
                        pointsPool.remove(p2)

            if not sizeChanged: # all connected points found
                if len(currentGroup) >= minimum_points_per_group: # add to group if number of points reached threshold - discard group if not enough points
                    foundGroups.append(currentGroup)
                currentGroup = set()
        """ Returns groups of points as list
        [{p1, p2, p3}, {p4, p5, p6, p7, p8}]
        """
        return foundGroups
