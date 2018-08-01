import random

from .unit import Unit
from .ids.unit_typeid import UnitTypeId
from .position import Point2, Point3
from typing import List, Dict, Set, Tuple, Any, Optional, Union # mypy type checking

class Units(list):
    """A collection for units. Makes it easy to select units by selectors."""
    @classmethod
    def from_proto(cls, units, game_data):
        return cls(
            (Unit(u, game_data) for u in units),
            game_data
        )

    def __init__(self, units, game_data):
        super().__init__(units)
        self.game_data = game_data

    def __call__(self, *args, **kwargs):
        return UnitSelection(self, *args, **kwargs)

    def select(self, *args, **kwargs):
        return UnitSelection(self, *args, **kwargs)

    def __or__(self, other: "Units") -> "Units":
        tags = {unit.tag for unit in self}
        units = self + [unit for unit in other if unit.tag not in tags]
        return Units(units, self.game_data)

    def __and__(self, other: "Units") -> "Units":
        tags = {unit.tag for unit in self}
        units = [unit for unit in other if unit.tag in tags]
        return Units(units, self.game_data)

    def __sub__(self, other: "Units") -> "Units":
        tags = {unit.tag for unit in other}
        units = [unit for unit in self if unit.tag not in tags]
        return Units(units, self.game_data)

    @property
    def amount(self) -> int:
        return len(self)

    @property
    def empty(self) -> bool:
        return self.amount == 0

    @property
    def exists(self) -> bool:
        return not self.empty

    def find_by_tag(self, tag) -> Optional[Unit]:
        for unit in self:
            if unit.tag == tag:
                return unit
        return None

    def by_tag(self, tag):
        unit = self.find_by_tag(tag)
        if unit is None:
            raise KeyError("Unit not found")
        return unit

    @property
    def first(self) -> Unit:
        assert self.exists
        return self[0]

    def take(self, n: int, require_all: bool=True) -> "Units":
        assert (not require_all) or len(self) >= n
        return self[:n]

    @property
    def random(self) -> Unit:
        assert self.exists
        return random.choice(self)

    def random_or(self, other: any) -> Unit:
        if self.exists:
            return random.choice(self)
        else:
            return other

    def random_group_of(self, n):
        assert 0 <= n <= self.amount
        if n == 0:
            return self.subgroup([])
        elif self.amount == n:
            return self
        else:
            return self.subgroup(random.sample(self, n))

    def in_attack_range_of(self, unit: Unit) -> "Units":
        """ Filters units that are in attack range of the unit in parameter """
        return self.filter(lambda x: unit.target_in_range(x))

    def closest_distance_to(self, position: Union[Unit, Point2, Point3]) -> Union[int, float]:
        """ Returns the distance between the closest unit from this group to the target unit """
        assert self.exists
        if isinstance(position, Unit):
            position = position.position
        return min({unit.position.to2.distance_to(position.to2) for unit in self})

    def closest_to(self, position: Union[Unit, Point2, Point3]) -> Unit:
        assert self.exists
        if isinstance(position, Unit):
            position = position.position
        return min(self, key=lambda unit: unit.position.to2.distance_to(position.to2))

    def furthest_to(self, position: Union[Unit, Point2, Point3]) -> Unit:
        """ Returns the distance between the furthest unit from this group to the target unit """
        assert self.exists
        if isinstance(position, Unit):
            position = position.position
        return max(self, key=lambda unit: unit.position.to2.distance_to(position.to2))

    def closer_than(self, distance: Union[int, float], position: Union[Unit, Point2, Point3]) -> "Units":
        if isinstance(position, Unit):
            position = position.position
        return self.filter(lambda unit: unit.position.to2.distance_to(position.to2) < distance)

    def further_than(self, distance: Union[int, float], position: Union[Unit, Point2, Point3]) -> "Units":
        if isinstance(position, Unit):
            position = position.position
        return self.filter(lambda unit: unit.position.to2.distance_to(position.to2) > distance)

    def subgroup(self, units):
        return Units(list(units), self.game_data)

    def filter(self, pred: callable) -> "Units":
        return self.subgroup(filter(pred, self))

    def sorted(self, keyfn: callable, reverse: bool=False) -> "Units":
        return self.subgroup(sorted(self, key=keyfn, reverse=reverse))

    def tags_in(self, other: Union[Set[int], List[int], Dict[int, Any]]) -> "Units":
        """ Filters all units that have their tags in the 'other' set/list/dict """
        # example: self.units(QUEEN).tags_in(self.queen_tags_assigned_to_do_injects)
        if isinstance(other, list):
            other = set(other)
        return self.filter(lambda unit: unit.tag in other)

    def tags_not_in(self, other: Union[Set[int], List[int], Dict[int, Any]]) -> "Units":
        """ Filters all units that have their tags not in the 'other' set/list/dict """
        # example: self.units(QUEEN).tags_not_in(self.queen_tags_assigned_to_do_injects)
        if isinstance(other, list):
            other = set(other)
        return self.filter(lambda unit: unit.tag not in other)

    def of_type(self, other: Union[UnitTypeId, Set[UnitTypeId], List[UnitTypeId], Dict[UnitTypeId, Any]]) -> "Units":
        """ Filters all units that are of a specific type """
        # example: self.units.of_type([ZERGLING, ROACH, HYDRALISK, BROODLORD])
        if isinstance(other, UnitTypeId):
            other = {other}
        if isinstance(other, list):
            other = set(other)
        return self.filter(lambda unit: unit.type_id in other)

    def exclude_type(self, other: Union[UnitTypeId, Set[UnitTypeId], List[UnitTypeId], Dict[UnitTypeId, Any]]) -> "Units":
        """ Filters all units that are not of a specific type """
        # example: self.known_enemy_units.exclude_type([OVERLORD])
        if isinstance(other, UnitTypeId):
            other = {other}
        if isinstance(other, list):
            other = set(other)
        return self.filter(lambda unit: unit.type_id not in other)

    @property
    def center(self) -> Point2:
        """ Returns the central point of all units in this list """
        assert self.exists
        pos = Point2((sum([unit.position.x for unit in self]) / self.amount, \
            sum([unit.position.y for unit in self]) / self.amount))
        return pos

    @property
    def selected(self) -> "Units":
        return self.filter(lambda unit: unit.is_selected)

    @property
    def tags(self) -> Set[int]:
        return {unit.tag for unit in self}

    @property
    def ready(self) -> "Units":
        return self.filter(lambda unit: unit.is_ready)

    @property
    def not_ready(self) -> "Units":
        return self.filter(lambda unit: not unit.is_ready)

    @property
    def noqueue(self) -> "Units":
        return self.filter(lambda unit: unit.noqueue)

    @property
    def idle(self) -> "Units":
        return self.filter(lambda unit: unit.is_idle)

    @property
    def owned(self) -> "Units":
        return self.filter(lambda unit: unit.is_mine)

    @property
    def enemy(self) -> "Units":
        return self.filter(lambda unit: unit.is_enemy)

    @property
    def flying(self) -> "Units":
        return self.filter(lambda unit: unit.is_flying)

    @property
    def not_flying(self) -> "Units":
        return self.filter(lambda unit: not unit.is_flying)

    @property
    def structure(self) -> "Units":
        return self.filter(lambda unit: unit.is_structure)

    @property
    def not_structure(self) -> "Units":
        return self.filter(lambda unit: not unit.is_structure)

    @property
    def gathering(self) -> "Units":
        return self.filter(lambda unit: unit.is_gathering)

    @property
    def mineral_field(self) -> "Units":
        return self.filter(lambda unit: unit.is_mineral_field)

    @property
    def vespene_geyser(self) -> "Units":
        return self.filter(lambda unit: unit.is_vespene_geyser)

    @property
    def prefer_idle(self) -> "Units":
        return self.sorted(lambda unit: unit.is_idle, reverse=True)

    def prefer_close_to(self, p: Union[Unit, Point2, Point3]) -> "Units":
        return self.sorted(lambda unit: unit.distance_to(p))


class UnitSelection(Units):
    def __init__(self, parent, unit_type_id=None):
        assert unit_type_id is None or isinstance(unit_type_id, (UnitTypeId, set))
        if isinstance(unit_type_id, set):
            assert all(isinstance(t, UnitTypeId) for t in unit_type_id)

        self.unit_type_id = unit_type_id
        super().__init__([u for u in parent if self.matches(u)], parent.game_data)

    def matches(self, unit):
        if self.unit_type_id is None:
            # empty selector matches everything
            return True
        elif isinstance(self.unit_type_id, set):
            return unit.type_id in self.unit_type_id
        else:
            return self.unit_type_id == unit.type_id
