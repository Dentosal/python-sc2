import random

from .util import name_matches
from .unit import Unit

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

    @property
    def amount(self):
        return len(self)

    @property
    def empty(self):
        return self.amount == 0

    @property
    def exists(self):
        return not self.empty

    @property
    def first(self):
        assert self.exists
        return self[0]

    @property
    def random(self):
        assert self.exists
        return random.choice(self)

    def closest_to(self, position):
        return min(self, key=lambda unit: unit.position.to2.distance_to(position))

    def closer_than(self, position, distance):
        return self.filter(lambda unit: unit.position.to2.distance_to(position) < distance)

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
    def idle(self):
        return self.filter(lambda unit: unit.is_idle)

    @property
    def owned(self):
        return self.filter(lambda unit: unit.is_mine)

    @property
    def prefer_idle(self):
        return self.sorted(lambda unit: unit.is_idle, reverse=True)

    def prefer_close_to(self, p):
        return self.sorted(lambda unit: unit.distance_to(p))

class UnitSelection(Units):
    def __init__(self, parent, name=None, name_exact=True):
        self.name = name
        super().__init__([u for u in parent if self.matches(u)], parent.game_data)

    def matches(self, unit):
        if self.name:
            return unit.matches(self.name)
        else:
            # empty selector matches everything
            return True

    @property
    def type_data(self):
        assert self.name
        for utd in self.game_data.units.values():
            if name_matches(utd.name, self.name):
                return utd
        raise KeyError

    @property
    def cost(self):
        return self.type_data.cost
