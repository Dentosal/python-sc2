from functools import lru_cache, reduce
from typing import List, Dict, Set, Tuple, Any, Optional, Union # mypy type checking

from .data import Attribute, Race
from .unit_command import UnitCommand

from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId

from .constants import ZERGLING

FREE_MORPH_ABILITY_CATEGORIES = [
    "Lower", "Raise", # SUPPLYDEPOT
    "Land",  "Lift",  # Flying buildings
]

def split_camel_case(text):
    """Splits words from CamelCase text."""
    return list(reduce(
        lambda a, b: (a + [b] if b.isupper() else a[:-1] + [a[-1] + b]),
        text,
        []
    ))

class GameData(object):
    def __init__(self, data):
        self.abilities = {a.ability_id: AbilityData(self, a) for a in data.abilities if AbilityData.id_exists(a.ability_id)}
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
            if unit.creation_ability is None:
                continue

            if not AbilityData.id_exists(unit.creation_ability.id.value):
                continue

            if unit.creation_ability.is_free_morph:
                continue

            if unit.creation_ability == ability:
                if unit.id == ZERGLING:
                    # HARD CODED: zerglings are generated in pairs
                    return Cost(
                        unit.cost.minerals * 2,
                        unit.cost.vespene * 2,
                        unit.cost.time
                    )
                # Correction for morphing units, e.g. orbital would return 550/0 instead of actual 150/0
                morph_cost = unit.morph_cost
                if morph_cost: # can be None
                    return morph_cost
                # Correction for zerg structures without morph: Extractor would return 75 instead of actual 25
                return unit.cost_zerg_corrected

        for upgrade in self.upgrades.values():
            if upgrade.research_ability == ability:
                return upgrade.cost

        return Cost(0, 0)

class AbilityData(object):
    @staticmethod
    def id_exists(ability_id):
        assert isinstance(ability_id, int), f"Wrong type: {ability_id} is not int"
        return ability_id != 0 and ability_id in (a.value for a in AbilityId)

    def __init__(self, game_data, proto):
        self._game_data = game_data
        self._proto = proto

        assert self.id != 0

    @property
    def id(self) -> AbilityId:
        if self._proto.remaps_to_ability_id:
            return AbilityId(self._proto.remaps_to_ability_id)
        return AbilityId(self._proto.ability_id)

    @property
    def link_name(self) -> str:
        """ For Stimpack this returns 'BarracksTechLabResearch' """
        return self._proto.button_name

    @property
    def button_name(self) -> str:
        """ For Stimpack this returns 'Stimpack' """
        return self._proto.button_name

    @property
    def friendly_name(self) -> str:
        """ For Stimpack this returns 'Research Stimpack' """
        return self._proto.friendly_name

    @property
    def is_free_morph(self) -> bool:
        parts = split_camel_case(self._proto.link_name)
        for p in parts:
            if p in FREE_MORPH_ABILITY_CATEGORIES:
                return True
        return False

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
    def id(self) -> UnitTypeId:
        return UnitTypeId(self._proto.unit_id)

    @property
    def name(self) -> str:
        return self._proto.name

    @property
    def creation_ability(self):
        if self._proto.ability_id == 0:
            return None
        if self._proto.ability_id not in self._game_data.abilities:
            return None
        return self._game_data.abilities[self._proto.ability_id]

    @property
    def attributes(self):
        return self._proto.attributes

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
    def cargo_size(self):
        """ How much cargo this unit uses up in cargo_space """
        return self._proto.cargo_size

    @property
    def tech_requirement(self) -> Optional[UnitTypeId]:
        """ Tech-building requirement of buildings - may work for units but unreliably """
        if self._proto.tech_requirement == 0:
            return None
        if self._proto.tech_requirement not in self._game_data.units:
            return None
        return UnitTypeId(self._proto.tech_requirement)

    @property
    def tech_alias(self) -> Optional[List[UnitTypeId]]:
        """ Building tech equality, e.g. OrbitalCommand is the same as CommandCenter """
        """ Building tech equality, e.g. Hive is the same as Lair and Hatchery """
        return_list = []
        for tech_alias in self._proto.tech_alias:
            if tech_alias in self._game_data.units:
                return_list.append(UnitTypeId(tech_alias))
        """ For Hive, this returns [UnitTypeId.Hatchery, UnitTypeId.Lair] """
        """ For SCV, this returns None """
        if return_list:
            return return_list
        return None

    @property
    def unit_alias(self) -> Optional[UnitTypeId]:
        """ Building type equality, e.g. FlyingOrbitalCommand is the same as OrbitalCommand """
        if self._proto.unit_alias == 0:
            return None
        if self._proto.unit_alias not in self._game_data.units:
            return None
        """ For flying OrbitalCommand, this returns UnitTypeId.OrbitalCommand """
        return UnitTypeId(self._proto.unit_alias)

    @property
    def race(self):
        return Race(self._proto.race)

    @property
    def cost(self) -> "Cost":
        return Cost(
            self._proto.mineral_cost,
            self._proto.vespene_cost,
            self._proto.build_time
        )

    @property
    def cost_zerg_corrected(self) -> "Cost":
        """ This returns 25 for extractor and 200 for spawning pool instead of 75 and 250 respectively """
        if self.race == Race.Zerg and Attribute.Structure.value in self.attributes:
            # a = self._game_data.units(UnitTypeId.ZERGLING)
            # print(a)
            # print(vars(a))
            return Cost(
                self._proto.mineral_cost - 50,
                self._proto.vespene_cost,
                self._proto.build_time
            )
        else:
            return self.cost

    @property
    def morph_cost(self) -> Optional["Cost"]:
        """ This returns 150 minerals for OrbitalCommand instead of 550 """
        if self.tech_alias is None:
            return None
        # Morphing a HIVE would have HATCHERY and LAIR in the tech alias - now subtract HIVE cost from LAIR cost instead of from HATCHERY cost
        tech_alias_cost_minerals = max([self._game_data.units[tech_alias.value].cost.minerals for tech_alias in self.tech_alias])
        tech_alias_cost_vespene = max([self._game_data.units[tech_alias.value].cost.vespene for tech_alias in self.tech_alias])
        return Cost(
                self._proto.mineral_cost - tech_alias_cost_minerals,
                self._proto.vespene_cost - tech_alias_cost_vespene,
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
    def research_ability(self) -> Optional[AbilityData]:
        if self._proto.ability_id == 0:
            return None
        if self._proto.ability_id not in self._game_data.abilities:
            return None
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

    def __eq__(self, other):
        return self.minerals == other.minerals and self.vespene == other.vespene

    def __ne__(self, other):
        return self.minerals != other.minerals or self.vespene != other.vespene

    def __repr__(self):
        return f"Cost({self.minerals}, {self.vespene})"
