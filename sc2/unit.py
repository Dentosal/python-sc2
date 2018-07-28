from s2clientprotocol import sc2api_pb2 as sc_pb, raw_pb2 as raw_pb
from sc2.ids.buff_id import BuffId

from .position import Point2, Point3
from .data import Alliance, Attribute, DisplayType, warpgate_abilities, TargetType, Race
from .game_data import GameData
from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId
from . import unit_command
from typing import List, Dict, Set, Tuple, Any, Optional, Union # mypy type checking

class Unit(object):
    def __init__(self, proto_data, game_data):
        assert isinstance(proto_data, raw_pb.Unit)
        assert isinstance(game_data, GameData)
        self._proto = proto_data
        self._game_data = game_data

    @property
    def type_id(self) -> UnitTypeId:
        return UnitTypeId(self._proto.unit_type)

    @property
    def _type_data(self) -> "UnitTypeData":
        return self._game_data.units[self._proto.unit_type]

    @property
    def is_snapshot(self) -> bool:
        return self._proto.display_type == DisplayType.Snapshot.value

    @property
    def is_visible(self) -> bool:
        return self._proto.display_type == DisplayType.Visible.value

    @property
    def alliance(self) -> Alliance:
        return self._proto.alliance

    @property
    def is_mine(self) -> bool:
        return self._proto.alliance == Alliance.Self.value

    @property
    def is_enemy(self) -> bool:
        return self._proto.alliance == Alliance.Enemy.value

    @property
    def tag(self) -> int:
        return self._proto.tag

    @property
    def owner_id(self) -> int:
        return self._proto.owner

    @property
    def position(self) -> Point2:
        """2d position of the unit."""
        return self.position3d.to2

    @property
    def position3d(self) -> Point3:
        """3d position of the unit."""
        return Point3.from_proto(self._proto.pos)

    def distance_to(self, p) -> Union[int, float]:
        return self.position.to2.distance_to(p.position.to2)

    @property
    def facing(self) -> Union[int, float]:
        return self._proto.facing

    @property
    def radius(self) -> Union[int, float]:
        return self._proto.radius

    @property
    def detect_range(self) -> Union[int, float]:
        return self._proto.detect_range

    @property
    def radar_range(self) -> Union[int, float]:
        return self._proto.radar_range

    @property
    def build_progress(self) -> Union[int, float]:
        return self._proto.build_progress

    @property
    def is_ready(self) -> bool:
        return self.build_progress == 1.0

    @property
    def cloak(self):
        return self._proto.cloak

    @property
    def is_blip(self) -> bool:
        """Detected by sensor tower."""
        return self._proto.is_blip

    @property
    def is_powered(self) -> bool:
        return self._proto.is_powered

    @property
    def is_burrowed(self) -> bool:
        return self._proto.is_burrowed

    @property
    def is_flying(self) -> bool:
        return self._proto.is_flying

    @property
    def is_structure(self) -> bool:
        return Attribute.Structure.value in self._type_data.attributes

    @property
    def is_light(self) -> bool:
        return Attribute.Light.value in self._type_data.attributes

    @property
    def is_armored(self) -> bool:
        return Attribute.Armored.value in self._type_data.attributes

    @property
    def is_biological(self) -> bool:
        return Attribute.Biological.value in self._type_data.attributes

    @property
    def is_mechanical(self) -> bool:
        return Attribute.Mechanical.value in self._type_data.attributes

    @property
    def is_robotic(self) -> bool:
        return Attribute.Robotic.value in self._type_data.attributes

    @property
    def is_massive(self) -> bool:
        return Attribute.Massive.value in self._type_data.attributes

    @property
    def is_mineral_field(self) -> bool:
        return self._type_data.has_minerals

    @property
    def is_vespene_geyser(self) -> bool:
        return self._type_data.has_vespene

    @property
    def tech_alias(self) -> Optional[List[UnitTypeId]]:
        """ Building tech equality, e.g. OrbitalCommand is the same as CommandCenter """
        """ For Hive, this returns [UnitTypeId.Hatchery, UnitTypeId.Lair] """
        """ For SCV, this returns None """
        return self._type_data.tech_alias

    @property
    def unit_alias(self) -> Optional[UnitTypeId]:
        """ Building type equality, e.g. FlyingOrbitalCommand is the same as OrbitalCommand """
        """ For flying OrbitalCommand, this returns UnitTypeId.OrbitalCommand """
        """ For SCV, this returns None """
        return self._type_data.unit_alias

    @property
    def race(self) -> Race:
        return Race(self._type_data._proto.race)

    @property
    def health(self) -> Union[int, float]:
        return self._proto.health

    @property
    def health_max(self) -> Union[int, float]:
        return self._proto.health_max

    @property
    def health_percentage(self) -> Union[int, float]:
        if self._proto.health_max == 0:
            return 0
        return self._proto.health / self._proto.health_max

    @property
    def shield(self) -> Union[int, float]:
        return self._proto.shield

    @property
    def shield_max(self) -> Union[int, float]:
        return self._proto.shield_max

    @property
    def shield_percentage(self) -> Union[int, float]:
        if self._proto.shield_max == 0:
            return 0
        return self._proto.shield / self._proto.shield_max

    @property
    def energy(self) -> Union[int, float]:
        return self._proto.energy

    @property
    def energy_max(self) -> Union[int, float]:
        return self._proto.energy_max

    @property
    def energy_percentage(self) -> Union[int, float]:
        if self._proto.energy_max == 0:
            return 0
        return self._proto.energy / self._proto.energy_max

    @property
    def mineral_contents(self) -> int:
        """ How many minerals a mineral field has left to mine from """
        return self._proto.mineral_contents

    @property
    def vespene_contents(self) -> int:
        """ How much gas is remaining in a geyser """
        return self._proto.vespene_contents

    @property
    def has_vespene(self) -> bool:
        """ Checks if a geyser has any gas remaining (can't build extractors on empty geysers), useful for lategame """
        return self._proto.vespene_contents > 0

    @property
    def weapon_cooldown(self) -> Union[int, float]:
        """ Returns some time (more than game loops) until the unit can fire again, returns -1 for units that can't attack
        Usage: 
        if unit.weapon_cooldown == 0:
            await self.do(unit.attack(target))
        elif unit.weapon_cooldown < 0:
            await self.do(unit.move(closest_allied_unit_because_cant_attack))
        else:
            await self.do(unit.move(retreatPosition))
        """
        if self.can_attack_ground or self.can_attack_air:
            return self._proto.weapon_cooldown
        return -1

    @property
    def cargo_size(self) -> Union[float, int]:
        """ How much cargo this unit uses up in cargo_space """
        return self._type_data.cargo_size

    @property
    def has_cargo(self) -> bool:
        return self._proto.cargo_space_taken > 0

    @property
    def cargo_used(self) -> Union[float, int]:
        return self._proto.cargo_space_taken

    @property
    def cargo_max(self) -> Union[float, int]:
        return self._proto.cargo_space_max

    # @property
    # def passengers(self):
    # TODO: convert each unit to passenger instance
    #     return self._proto.passengers

    # TODO: retrieve all passenger tags in one call

    @property
    def can_attack_ground(self) -> bool:
        # See data_pb2.py line 141 for info on weapon data
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [TargetType.Ground.value, TargetType.Any.value]), None)
            return weapon is not None
        return False
    
    @property
    def ground_dps(self) -> Union[int, float]:
        """ Does not include upgrades """
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [TargetType.Ground.value, TargetType.Any.value]), None)
            if weapon:
                return (weapon.damage * weapon.attacks) / weapon.speed
        return 0

    @property
    def ground_range(self) -> Union[int, float]:
        """ Does not include upgrades """
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [TargetType.Ground.value, TargetType.Any.value]), None)
            if weapon:
                return weapon.range
        return 0

    @property
    def can_attack_air(self) -> bool:
        """ Does not include upgrades """
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [TargetType.Air.value, TargetType.Any.value]), None)
            return weapon is not None
        return False

    @property
    def air_dps(self) -> Union[int, float]:
        """ Does not include upgrades """
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [TargetType.Air.value, TargetType.Any.value]), None)
            if weapon:
                return (weapon.damage * weapon.attacks) / weapon.speed
        return 0

    @property
    def air_range(self) -> Union[int, float]:
        """ Does not include upgrades """
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [TargetType.Air.value, TargetType.Any.value]), None)
            if weapon:
                return weapon.range
        return 0

    def target_in_range(self, target: "Unit", bonus_distance: Union[int, float]=0) -> bool:
        """ Includes the target's radius when calculating distance to target """
        if self.can_attack_ground and not target.is_flying:
            unit_attack_range = self.ground_range
        elif self.can_attack_air and target.is_flying:
            unit_attack_range = self.air_range
        else:
            unit_attack_range = -1
        return self.distance_to(target) + bonus_distance <= target.radius + unit_attack_range

    @property
    def armor(self) -> Union[int, float]:
        """ Does not include upgrades """
        return self._type_data._proto.armor

    @property
    def sight_range(self) -> Union[int, float]:
        return self._type_data._proto.sight_range

    @property
    def movement_speed(self) -> Union[int, float]:
        return self._type_data._proto.movement_speed

    @property
    def is_carrying_minerals(self) -> bool:
        return self.has_buff(BuffId.CARRYMINERALFIELDMINERALS) or self.has_buff(BuffId.CARRYHIGHYIELDMINERALFIELDMINERALS)

    @property
    def is_carrying_vespene(self) -> bool:
        return self.has_buff(BuffId.CARRYHARVESTABLEVESPENEGEYSERGAS) or self.has_buff(BuffId.CARRYHARVESTABLEVESPENEGEYSERGASPROTOSS) or self.has_buff(BuffId.CARRYHARVESTABLEVESPENEGEYSERGASZERG)

    @property
    def is_selected(self) -> bool:
        return self._proto.is_selected

    @property
    def orders(self) -> List["UnitOrder"]:
        return [UnitOrder.from_proto(o, self._game_data) for o in self._proto.orders]

    @property
    def noqueue(self) -> bool:
        return len(self.orders) == 0

    @property
    def is_moving(self) -> bool:
        return len(self.orders) > 0 and self.orders[0].ability.id in [AbilityId.MOVE]

    @property
    def is_attacking(self) -> bool:
        return len(self.orders) > 0 and self.orders[0].ability.id in [AbilityId.ATTACK, AbilityId.ATTACK_ATTACK, AbilityId.ATTACK_ATTACKTOWARDS, AbilityId.ATTACK_ATTACKBARRAGE, AbilityId.SCAN_MOVE]

    @property
    def is_gathering(self) -> bool:
        """ Checks if a unit is on its way to a mineral field / vespene geyser to mine """
        return len(self.orders) > 0 and self.orders[0].ability.id in [AbilityId.HARVEST_GATHER]

    @property
    def order_target(self) -> Optional[Union[int, Point2, Point3]]:
        """ Returns the target tag (if it is a Unit) or Point2 (if it is a Position) from the first order """
        if len(self.orders) > 0:
            if isinstance(self.orders[0].target, int):
                return self.orders[0].target
            else:
                return Point2.from_proto(self.orders[0].target)
        return None

    @property
    def is_idle(self) -> bool:
        return not self.orders

    @property
    def add_on_tag(self) -> int:
        return self._proto.add_on_tag

    @property
    def add_on_land_position(self) -> Point2:
        """ If unit is addon (techlab or reactor), returns the position where a terran building has to land to connect to addon """
        return self.position.offset(Point2((-2.5, 0.5)))

    @property
    def has_add_on(self) -> bool:
        return self.add_on_tag != 0

    @property
    def assigned_harvesters(self) -> int:
        return self._proto.assigned_harvesters

    @property
    def ideal_harvesters(self) -> int:
        return self._proto.ideal_harvesters

    @property
    def surplus_harvesters(self) -> int:
        """ Returns a positive number if it has too many harvesters mining, a negative number if it has too few mining """
        return -(self._proto.ideal_harvesters - self._proto.assigned_harvesters)

    @property
    def name(self):
        return self._type_data.name

    def train(self, unit, *args, **kwargs):
        return self(self._game_data.units[unit.value].creation_ability.id, *args, **kwargs)

    def build(self, unit, *args, **kwargs):
        return self(self._game_data.units[unit.value].creation_ability.id, *args, **kwargs)

    def research(self, upgrade, *args, **kwargs):
        """ Requires UpgradeId to be passed instead of AbilityId """
        return self(self._game_data.upgrades[upgrade.value].research_ability.id, *args, **kwargs)

    def has_buff(self, buff):
        assert isinstance(buff, BuffId)

        return buff.value in self._proto.buff_ids

    def warp_in(self, unit, placement, *args, **kwargs):
        normal_creation_ability = self._game_data.units[unit.value].creation_ability.id
        return self(warpgate_abilities[normal_creation_ability], placement, *args, **kwargs)

    def attack(self, *args, **kwargs):
        return self(AbilityId.ATTACK, *args, **kwargs)

    def gather(self, *args, **kwargs):
        return self(AbilityId.HARVEST_GATHER, *args, **kwargs)

    def return_resource(self, *args, **kwargs):
        return self(AbilityId.HARVEST_RETURN, *args, **kwargs)

    def move(self, *args, **kwargs):
        return self(AbilityId.MOVE, *args, **kwargs)

    def hold_position(self, *args, **kwargs):
        return self(AbilityId.HOLDPOSITION, *args, **kwargs)

    def stop(self, *args, **kwargs):
        return self(AbilityId.STOP, *args, **kwargs)

    def __hash__(self):
        return hash(self.tag)

    def __call__(self, ability, *args, **kwargs):
        return unit_command.UnitCommand(ability, self, *args, **kwargs)

    def __repr__(self):
        return f"Unit(name={self.name !r}, tag={self.tag})"

class UnitOrder(object):
    @classmethod
    def from_proto(cls, proto, game_data):
        return cls(
            game_data.abilities[proto.ability_id],
            (proto.target_world_space_pos
                if proto.HasField("target_world_space_pos") else
                proto.target_unit_tag),
            proto.progress
        )

    def __init__(self, ability, target, progress=None):
        self.ability = ability
        self.target = target
        self.progress = progress

    def __repr__(self):
        return f"UnitOrder({self.ability}, {self.target}, {self.progress})"
