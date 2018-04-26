import random

from .unit import Unit
from .ids.unit_typeid import UnitTypeId

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

    def __or__(self, other):
        tags = {unit.tag for unit in self}
        units = self + [unit for unit in other if unit.tag not in tags]
        return Units(units, self.game_data)

    def __and__(self, other):
        tags = {unit.tag for unit in self}
        units = [unit for unit in other if unit.tag in tags]
        return Units(units, self.game_data)

    def __sub__(self, other):
        tags = {unit.tag for unit in other}
        units = [unit for unit in self if unit.tag not in tags]
        return Units(units, self.game_data)

    @property
    def amount(self):
        return len(self)

    @property
    def empty(self):
        return self.amount == 0

    @property
    def exists(self):
        return not self.empty

    def find_by_tag(self, tag):
        for unit in self:
            if unit.tag == tag:
                return unit
        return None

    def by_tag(self, tag):
        unit = find_by_tag(tag)
        if unit is None:
            raise KeyError("Unit not found")
        return unit

    @property
    def first(self):
        assert self.exists
        return self[0]

    def take(self, n, require_all=True):
        assert (not require_all) or len(self) >= n
        return self[:n]

    @property
    def random(self):
        assert self.exists
        return random.choice(self)

    def random_or(self, other):
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

    def closest_to(self, position):
        if isinstance(position, Unit):
            position = position.position
        return min(self, key=lambda unit: unit.position.to2.distance_to(position.to2))

    def closer_than(self, distance, position):
        if isinstance(position, Unit):
            position = position.position
        return self.filter(lambda unit: unit.position.to2.distance_to(position.to2) < distance)

    def subgroup(self, units):
        return Units(list(units), self.game_data)

    def filter(self, pred):
        return self.subgroup(filter(pred, self))

    def sorted(self, keyfn, reverse=False):
        return self.subgroup(sorted(self, key=keyfn, reverse=reverse))

    @property
    def ready(self):
        return self.filter(lambda unit: unit.is_ready)

    @property
    def not_ready(self):
        return self.filter(lambda unit: not unit.is_ready)

    @property
    def noqueue(self):
        return self.filter(lambda unit: unit.noqueue)

    @property
    def idle(self):
        return self.filter(lambda unit: unit.is_idle)

    @property
    def owned(self):
        return self.filter(lambda unit: unit.is_mine)

    @property
    def enemy(self):
        return self.filter(lambda unit: unit.is_enemy)

    @property
    def structure(self):
        return self.filter(lambda unit: unit.is_structure)

    @property
    def not_structure(self):
        return self.filter(lambda unit: not unit.is_structure)

    @property
    def mineral_field(self):
        return self.filter(lambda unit: unit.is_mineral_field)

    @property
    def vespene_geyser(self):
        return self.filter(lambda unit: unit.is_vespene_geyser)

    @property
    def prefer_idle(self):
        return self.sorted(lambda unit: unit.is_idle, reverse=True)

    def prefer_close_to(self, p):
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
