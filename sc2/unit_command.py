from .position import Point2
from .ids.ability_id import AbilityId
from . import unit as unit_module

class UnitCommand:
    def __init__(self, ability, unit, target=None, queue=False):
        assert ability in AbilityId
        assert isinstance(unit, unit_module.Unit)
        assert target is None or isinstance(target, (Point2, unit_module.Unit))
        assert isinstance(queue, bool)
        self.ability = ability
        self.unit = unit
        self.target = target
        self.queue = queue

    @property
    def combining_tuple(self):
        return (self.ability, self.target, self.queue)

    def __repr__(self):
        return f"UnitCommand({self.ability}, {self.unit}, {self.target}, {self.queue})"
