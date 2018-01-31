from functools import lru_cache

from .data import Attribute
from .unit_command import UnitCommand

from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId

from .constants import ZERGLING

class GameData(object):
    def __init__(self, data):
        self.abilities = {a.ability_id: AbilityData(self, a) for a in data.abilities}
        self.units = {u.unit_id: UnitTypeData(self, u) for u in data.units if u.available}
        self.upgrades = {u.upgrade_id: UpgradeData(self, u) for u in data.upgrades}

    @lru_cache(maxsize=256)
    def calculate_ability_cost(self, ability):
        if isinstance(ability, AbilityId):
            ability = self.abilities[ability.value]
        elif isinstance(ability, UnitCommand):
            ability = self.abilities[ability.ability.value]

        assert isinstance(ability, AbilityData), f"C: {ability}"

        for unit in self.units.values():
            if unit.creation_ability == ability:
                if unit.id == ZERGLING:
                    # HARD CODED: zerglings are generated in pairs
                    return Cost(
                        unit.cost.minerals * 2,
                        unit.cost.vespene * 2,
                        unit.cost.time
                    )
                return unit.cost

        for upgrade in self.upgrades.values():
            if upgrade.research_ability == ability:
                return upgrade.cost

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
        return self._game_data.calculate_ability_cost(self.id)

    def __repr__(self):
        return f"AbilityData(name={self._proto.button_name})"

class UnitTypeData(object):
    def __init__(self, game_data, proto):
        self._game_data = game_data
        self._proto = proto

    @property
    def id(self):
        return UnitTypeId(self._proto.unit_id)

    @property
    def name(self):
        return self._proto.name

    @property
    def creation_ability(self):
        return self._game_data.abilities[self._proto.ability_id]

    @property
    def attributes(self):
        return self._proto.attributes

    @property
    def has_attribute(self, attr):
        assert isinstance(attr, Attribute)
        return attr in self.attributes

    @property
    def has_minerals(self):
        return self._proto.has_minerals

    @property
    def has_vespene(self):
        return self._proto.has_vespene

    @property
    def cost(self):
        return Cost(
            self._proto.mineral_cost,
            self._proto.vespene_cost,
            self._proto.build_time
        )

class UpgradeData(object):
    def __init__(self, game_data, proto):
        self._game_data = game_data
        self._proto = proto

    @property
    def name(self):
        return self._proto.name

    @property
    def research_ability(self):
        return self._game_data.abilities[self._proto.ability_id]

    @property
    def cost(self):
        return Cost(
            self._proto.mineral_cost,
            self._proto.vespene_cost,
            self._proto.research_time
        )

class Cost(object):
    def __init__(self, minerals, vespene, time=None):
        self.minerals = minerals
        self.vespene = vespene
        self.time = time

    def __repr__(self):
        return f"Cost({self.minerals}, {self.vespene})"
