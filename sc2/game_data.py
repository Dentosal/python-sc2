from .data import Attribute

from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId

class GameData(object):
    def __init__(self, data):
        self.abilities = {a.ability_id: AbilityData(self, a) for a in data.abilities if a.available}
        self.units = {u.unit_id: UnitTypeData(self, u) for u in data.units if u.available}

    def calculate_ability_cost(self, ability):
        name = ability.name.lower().split("_")
        if len(name) == 2 and name[0] in ("build", "train"):
            for unit_type in self.units.values():
                if unit_type.name.lower().replace(" ", "") == name[1].lower().replace(" ", ""):
                    return unit_type.cost
            raise RuntimeError(f"Unable unknown unit {name[1]}")
        return Cost(0, 0)


class AbilityData(object):
    def __init__(self, game_data, proto):
        self._game_data = game_data
        self._proto = proto

    @property
    def id(self):
        if self._proto.remaps_to_ability_id:
            return AbilityId(self._proto.remaps_to_ability_id)
        return AbilityId(self._proto.ability_id)

    @property
    def cost(self):
        return self._game_data.calculate_ability_cost(self._proto.button_name)

    def __repr__(self):
        return f"AbilityData(name={self._proto.button_name})"

class UnitTypeData(object):
    def __init__(self, game_data, proto):
        self._game_data = game_data
        self._proto = proto

    @property
    def name(self):
        return self._proto.name

    @property # FIXME: waiting for changes, see tmpfix.py
    def ability_id(self):
        return self._proto.ability_id

    @property
    def attributes(self):
        return self._proto.attributes

    @property
    def has_attribute(self, attr):
        assert isinstance(attr, Attribute)
        return attr in self.attributes

    @property
    def cost(self):
        return Cost(
            self._proto.mineral_cost,
            self._proto.vespene_cost
        )

class Cost(object):
    def __init__(self, minerals, vespene, time=None):
        self.minerals = minerals
        self.vespene = vespene
        self.time = time
