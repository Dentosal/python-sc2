from typing import Any, Dict, List, Optional, Set, Tuple, Union  # mypy type checking

from sc2.ids.buff_id import BuffId

from .cache import property_mutable_cache, property_immutable_cache
from . import unit_command
from .data import Alliance, Attribute, CloakState, DisplayType, Race, TargetType, warpgate_abilities
from .game_data import GameData
from .ids.ability_id import AbilityId
from .ids.unit_typeid import UnitTypeId
from .position import Point2, Point3


class PassengerUnit:
    def __init__(self, proto_data, game_data):
        assert isinstance(game_data, GameData)
        self._proto = proto_data
        self._game_data = game_data
        self.cache = {}

    def __repr__(self):
        """ Will return string of this form: Unit(name='SCV', tag=4396941328) """
        return f"{self.__class__.__name__}(name={self.name !r}, tag={self.tag})"

    @property
    def type_id(self) -> UnitTypeId:
        """ UnitTypeId found in sc2/ids/unit_typeid
        Caches all type_ids of the same unit type"""
        unit_type = self._proto.unit_type
        if unit_type not in self._game_data.unit_types:
            self._game_data.unit_types[unit_type] = UnitTypeId(unit_type)
        return self._game_data.unit_types[unit_type]

    @property_immutable_cache
    def _type_data(self) -> "UnitTypeData":
        return self._game_data.units[self._proto.unit_type]

    @property_immutable_cache
    def name(self) -> str:
        return self._type_data.name

    @property_immutable_cache
    def race(self) -> Race:
        return Race(self._type_data._proto.race)

    @property_immutable_cache
    def tag(self) -> int:
        return self._proto.tag

    @property_immutable_cache
    def is_structure(self) -> bool:
        return Attribute.Structure.value in self._type_data.attributes

    @property_immutable_cache
    def is_light(self) -> bool:
        return Attribute.Light.value in self._type_data.attributes

    @property_immutable_cache
    def is_armored(self) -> bool:
        return Attribute.Armored.value in self._type_data.attributes

    @property_immutable_cache
    def is_biological(self) -> bool:
        return Attribute.Biological.value in self._type_data.attributes

    @property_immutable_cache
    def is_mechanical(self) -> bool:
        return Attribute.Mechanical.value in self._type_data.attributes

    @property_immutable_cache
    def is_robotic(self) -> bool:
        return Attribute.Robotic.value in self._type_data.attributes

    @property_immutable_cache
    def is_massive(self) -> bool:
        return Attribute.Massive.value in self._type_data.attributes

    @property_immutable_cache
    def is_psionic(self) -> bool:
        return Attribute.Psionic.value in self._type_data.attributes

    @property_immutable_cache
    def cargo_size(self) -> Union[float, int]:
        """ How much cargo this unit uses up in cargo_space """
        return self._type_data.cargo_size

    @property_immutable_cache
    def _weapons(self):
        if hasattr(self._type_data._proto, "weapons"):
            return self._type_data._proto.weapons
        return False

    @property_immutable_cache
    def can_attack(self) -> bool:
        """ Can attack at all"""
        return bool(self._weapons)

    @property_immutable_cache
    def can_attack_ground(self) -> bool:
        if self._weapons:
            weapon = next(
                (weapon for weapon in self._weapons if weapon.type in {TargetType.Ground.value, TargetType.Any.value}),
                None,
            )
            return weapon is not None
        return False

    @property_immutable_cache
    def ground_dps(self) -> Union[int, float]:
        """ Does not include upgrades """
        if self._weapons:
            weapon = next(
                (weapon for weapon in self._weapons if weapon.type in {TargetType.Ground.value, TargetType.Any.value}),
                None,
            )
            if weapon:
                return (weapon.damage * weapon.attacks) / weapon.speed
        return 0

    @property_immutable_cache
    def ground_range(self) -> Union[int, float]:
        """ Does not include upgrades """
        if self._weapons:
            weapon = next(
                (weapon for weapon in self._weapons if weapon.type in {TargetType.Ground.value, TargetType.Any.value}),
                None,
            )
            if weapon:
                return weapon.range
        return 0

    @property_immutable_cache
    def can_attack_air(self) -> bool:
        """ Does not include upgrades """
        if self._weapons:
            weapon = next(
                (weapon for weapon in self._weapons if weapon.type in {TargetType.Air.value, TargetType.Any.value}),
                None,
            )
            return weapon is not None
        return False

    @property_immutable_cache
    def air_dps(self) -> Union[int, float]:
        """ Does not include upgrades """
        if self._weapons:
            weapon = next(
                (weapon for weapon in self._weapons if weapon.type in {TargetType.Air.value, TargetType.Any.value}),
                None,
            )
            if weapon:
                return (weapon.damage * weapon.attacks) / weapon.speed
        return 0

    @property_immutable_cache
    def air_range(self) -> Union[int, float]:
        """ Does not include upgrades """
        if self._weapons:
            weapon = next(
                (weapon for weapon in self._weapons if weapon.type in {TargetType.Air.value, TargetType.Any.value}),
                None,
            )
            if weapon:
                return weapon.range
        return 0

    @property_immutable_cache
    def bonus_damage(self):
        """ Returns a tuple of form 'bonus damage, armor type' if unit does bonus damage against armor type
        Light = 1; Armored = 2; Biological = 3; Mechanical = 4; Robotic = 5; Psionic = 6; Massive = 7;
        Structure = 8; Hover = 9; Heroic = 10; Summoned = 11 """
        # TODO Consider unit with ability attacks like Oracle, Thor, Baneling
        if self._weapons:
            for weapon in self._weapons:
                if weapon.damage_bonus:
                    b = weapon.damage_bonus[0]
                    return b.bonus, b.attribute

    @property_immutable_cache
    def armor(self) -> Union[int, float]:
        """ Does not include upgrades """
        return self._type_data._proto.armor

    @property_immutable_cache
    def sight_range(self) -> Union[int, float]:
        return self._type_data._proto.sight_range

    @property_immutable_cache
    def movement_speed(self) -> Union[int, float]:
        # TODO INCLUDE BUFFS AND DEBUFFS
        return self._type_data._proto.movement_speed

    @property_immutable_cache
    def health(self) -> Union[int, float]:
        """ Does not include shields """
        return self._proto.health

    @property_immutable_cache
    def health_max(self) -> Union[int, float]:
        """ Does not include shields """
        return self._proto.health_max

    @property_immutable_cache
    def health_percentage(self) -> Union[int, float]:
        """ Does not include shields """
        if self._proto.health_max == 0:
            return 0
        return self._proto.health / self._proto.health_max

    @property_immutable_cache
    def shield(self) -> Union[int, float]:
        return self._proto.shield

    @property_immutable_cache
    def shield_max(self) -> Union[int, float]:
        return self._proto.shield_max

    @property_immutable_cache
    def shield_percentage(self) -> Union[int, float]:
        if self._proto.shield_max == 0:
            return 0
        return self._proto.shield / self._proto.shield_max

    @property_immutable_cache
    def energy(self) -> Union[int, float]:
        return self._proto.energy

    @property_immutable_cache
    def energy_max(self) -> Union[int, float]:
        return self._proto.energy_max

    @property_immutable_cache
    def energy_percentage(self) -> Union[int, float]:
        if self._proto.energy_max == 0:
            return 0
        return self._proto.energy / self._proto.energy_max


class Unit(PassengerUnit):
    @property_immutable_cache
    def is_snapshot(self) -> bool:
        return self._proto.display_type == DisplayType.Snapshot.value

    @property_immutable_cache
    def is_visible(self) -> bool:
        return self._proto.display_type == DisplayType.Visible.value

    @property_immutable_cache
    def alliance(self) -> Alliance:
        return self._proto.alliance

    @property_immutable_cache
    def is_mine(self) -> bool:
        return self._proto.alliance == Alliance.Self.value

    @property_immutable_cache
    def is_enemy(self) -> bool:
        return self._proto.alliance == Alliance.Enemy.value

    @property_immutable_cache
    def owner_id(self) -> int:
        return self._proto.owner

    @property_immutable_cache
    def position(self) -> Point2:
        return Point2((self._proto.pos.x, self._proto.pos.y))

    @property_immutable_cache
    def position3d(self) -> Point3:
        """3d position of the unit."""
        return Point3.from_proto(self._proto.pos)

    def distance_to(self, p: Union["Unit", Point2, Point3], bot: "BotAI" = None) -> Union[int, float]:
        """ Using the 2d distance between self and p. To calculate the 3d distance,
        use unit.position3d.distance_to(p) """
        if bot and isinstance(p, Unit):
            index = bot.distances_tag_dict
            return (bot.unit_distances_dict[index[self.tag]][index[p.tag]]) ** 0.5
        return self.position.distance_to_point2(p.position)

    @property_immutable_cache
    def facing(self) -> Union[int, float]:
        """ Returns float in range [0,2p). 0 means in direction of x axis."""
        return self._proto.facing

    @property_immutable_cache
    def radius(self) -> Union[int, float]:
        """ Half of unit size. See https://liquipedia.net/starcraft2/Unit_Statistics_(Legacy_of_the_Void) """
        return self._proto.radius

    @property_immutable_cache
    def detect_range(self) -> Union[int, float]:
        return self._proto.detect_range

    @property_immutable_cache
    def radar_range(self) -> Union[int, float]:
        return self._proto.radar_range

    @property_immutable_cache
    def build_progress(self) -> Union[int, float]:
        """ Returns completion in range [0,1]."""
        return self._proto.build_progress

    @property_immutable_cache
    def is_ready(self) -> bool:
        return self.build_progress == 1

    @property_immutable_cache
    def cloak(self) -> CloakState:
        """ Returns cloak state.
        See https://github.com/Blizzard/s2client-api/blob/d9ba0a33d6ce9d233c2a4ee988360c188fbe9dbf/include/sc2api/sc2_unit.h#L95 """
        return self._proto.cloak

    @property_immutable_cache
    def is_cloaked(self) -> bool:
        return self._proto.cloak in {CloakState.Cloaked.value, CloakState.CloakedDetected.value}

    @property_immutable_cache
    def is_blip(self) -> bool:
        """ Detected by sensor tower. """
        return self._proto.is_blip

    @property_immutable_cache
    def is_powered(self) -> bool:
        """ Is powered by a pylon nearby. """
        return self._proto.is_powered

    @property_immutable_cache
    def is_burrowed(self) -> bool:
        return self._proto.is_burrowed

    @property_immutable_cache
    def is_flying(self) -> bool:
        return self._proto.is_flying

    @property_immutable_cache
    def is_psionic(self) -> bool:
        return Attribute.Psionic.value in self._type_data.attributes

    @property_immutable_cache
    def is_mineral_field(self) -> bool:
        return self._type_data.has_minerals

    @property_immutable_cache
    def is_vespene_geyser(self) -> bool:
        return self._type_data.has_vespene

    @property
    def tech_alias(self) -> Optional[List[UnitTypeId]]:
        """ Building tech equality, e.g. OrbitalCommand is the same as CommandCenter
        For Hive, this returns [UnitTypeId.Hatchery, UnitTypeId.Lair]
        For SCV, this returns None """
        return self._type_data.tech_alias

    @property_immutable_cache
    def unit_alias(self) -> Optional[UnitTypeId]:
        """ Building type equality, e.g. FlyingOrbitalCommand is the same as OrbitalCommand
        For flying OrbitalCommand, this returns UnitTypeId.OrbitalCommand
        For SCV, this returns None """
        return self._type_data.unit_alias

    @property_immutable_cache
    def mineral_contents(self) -> int:
        """ How many minerals a mineral field has left to mine """
        return self._proto.mineral_contents

    @property_immutable_cache
    def vespene_contents(self) -> int:
        """ How much gas is remaining in a geyser """
        return self._proto.vespene_contents

    @property_immutable_cache
    def has_vespene(self) -> bool:
        """ Checks if a geyser has any gas remaining (can't build extractors on empty geysers), useful for lategame """
        return bool(self._proto.vespene_contents)

    @property_immutable_cache
    def weapon_cooldown(self) -> Union[int, float]:
        """ Returns some time (more than game loops) until the unit can fire again,
        returns -1 for units that can't attack.
        Usage:
        if unit.weapon_cooldown == 0:
            await self.do(unit.attack(target))
        elif unit.weapon_cooldown < 0:
            await self.do(unit.move(closest_allied_unit_because_cant_attack))
        else:
            await self.do(unit.move(retreatPosition))
        """
        if self.can_attack:
            return self._proto.weapon_cooldown
        return -1

    @property_immutable_cache
    def has_cargo(self) -> bool:
        """ If this unit has units loaded """
        return bool(self._proto.cargo_space_taken)

    @property_immutable_cache
    def cargo_used(self) -> Union[float, int]:
        """ How much cargo space is used (some units take up more than 1 space) """
        return self._proto.cargo_space_taken

    @property_immutable_cache
    def cargo_max(self) -> Union[float, int]:
        """ How much cargo space is totally available - CC: 5, Bunker: 4, Medivac: 8
        and Bunker can only load infantry, CC only SCVs """
        return self._proto.cargo_space_max

    @property_mutable_cache
    def passengers(self) -> Set["PassengerUnit"]:
        """ Units inside a Bunker, CommandCenter, Nydus, Medivac, WarpPrism, Overlord """
        return {PassengerUnit(unit, self._game_data) for unit in self._proto.passengers}

    @property_mutable_cache
    def passengers_tags(self) -> Set[int]:
        return {unit.tag for unit in self._proto.passengers}

    def target_in_range(self, target: "Unit", bonus_distance: Union[int, float] = 0) -> bool:
        """ Includes the target's radius when calculating distance to target """
        if self.can_attack_ground and not target.is_flying:
            unit_attack_range = self.ground_range
        elif self.can_attack_air and (target.is_flying or target.type_id == UnitTypeId.COLOSSUS):
            unit_attack_range = self.air_range
        else:
            unit_attack_range = -1
        return (
            self.position._distance_squared(target.position)
            <= (self.radius + target.radius + unit_attack_range - bonus_distance) ** 2
        )

    @property_immutable_cache
    def is_carrying_minerals(self) -> bool:
        """ Checks if a worker or MULE is carrying (gold-)minerals. """
        return any(
            buff.value in self._proto.buff_ids
            for buff in {BuffId.CARRYMINERALFIELDMINERALS, BuffId.CARRYHIGHYIELDMINERALFIELDMINERALS}
        )

    @property_immutable_cache
    def is_carrying_vespene(self) -> bool:
        """ Checks if a worker is carrying vespene. """
        return any(
            buff.value in self._proto.buff_ids
            for buff in {
                BuffId.CARRYHARVESTABLEVESPENEGEYSERGAS,
                BuffId.CARRYHARVESTABLEVESPENEGEYSERGASPROTOSS,
                BuffId.CARRYHARVESTABLEVESPENEGEYSERGASZERG,
            }
        )

    @property_immutable_cache
    def is_selected(self) -> bool:
        return self._proto.is_selected

    @property_mutable_cache
    def orders(self) -> List["UnitOrder"]:
        return [UnitOrder.from_proto(o, self._game_data) for o in self._proto.orders]

    @property_immutable_cache
    def noqueue(self) -> bool:
        return not self.orders

    @property_immutable_cache
    def is_moving(self) -> bool:
        return self.orders and self.orders[0].ability.id is AbilityId.MOVE

    @property_immutable_cache
    def is_attacking(self) -> bool:
        return self.orders and self.orders[0].ability.id in {
            AbilityId.ATTACK,
            AbilityId.ATTACK_ATTACK,
            AbilityId.ATTACK_ATTACKTOWARDS,
            AbilityId.ATTACK_ATTACKBARRAGE,
            AbilityId.SCAN_MOVE,
        }

    @property_immutable_cache
    def is_patrolling(self) -> bool:
        """ Checks if a unit is patrolling. """
        return self.orders and self.orders[0].ability.id is AbilityId.PATROL

    @property_immutable_cache
    def is_gathering(self) -> bool:
        """ Checks if a unit is on its way to a mineral field / vespene geyser to mine. """
        return self.orders and self.orders[0].ability.id is AbilityId.HARVEST_GATHER

    @property_immutable_cache
    def is_returning(self) -> bool:
        """ Checks if a unit is returning from mineral field / vespene geyser to deliver resources to townhall. """
        return self.orders and self.orders[0].ability.id is AbilityId.HARVEST_RETURN

    @property_immutable_cache
    def is_collecting(self) -> bool:
        """ Combines the two properties above. """
        return self.orders and self.orders[0].ability.id in {AbilityId.HARVEST_GATHER, AbilityId.HARVEST_RETURN}

    @property_immutable_cache
    def is_constructing_scv(self) -> bool:
        """ Checks if the unit is an SCV that is currently building. """
        return self.orders and self.orders[0].ability.id in {
            AbilityId.TERRANBUILD_ARMORY,
            AbilityId.TERRANBUILD_BARRACKS,
            AbilityId.TERRANBUILD_BUNKER,
            AbilityId.TERRANBUILD_COMMANDCENTER,
            AbilityId.TERRANBUILD_ENGINEERINGBAY,
            AbilityId.TERRANBUILD_FACTORY,
            AbilityId.TERRANBUILD_FUSIONCORE,
            AbilityId.TERRANBUILD_GHOSTACADEMY,
            AbilityId.TERRANBUILD_MISSILETURRET,
            AbilityId.TERRANBUILD_REFINERY,
            AbilityId.TERRANBUILD_SENSORTOWER,
            AbilityId.TERRANBUILD_STARPORT,
            AbilityId.TERRANBUILD_SUPPLYDEPOT,
        }

    @property_immutable_cache
    def is_repairing(self) -> bool:
        return self.orders and self.orders[0].ability.id in {
            AbilityId.EFFECT_REPAIR,
            AbilityId.EFFECT_REPAIR_MULE,
            AbilityId.EFFECT_REPAIR_SCV,
        }

    @property_immutable_cache
    def order_target(self) -> Optional[Union[int, Point2]]:
        """ Returns the target tag (if it is a Unit) or Point2 (if it is a Position)
        from the first order, returns None if the unit is idle """
        if self.orders:
            if isinstance(self.orders[0].target, int):
                return self.orders[0].target
            else:
                return Point2.from_proto(self.orders[0].target)
        return None

    @property_immutable_cache
    def is_idle(self) -> bool:
        return not self.orders

    @property_immutable_cache
    def add_on_tag(self) -> int:
        return self._proto.add_on_tag

    @property_immutable_cache
    def add_on_land_position(self) -> Point2:
        """ If unit is addon (techlab or reactor), returns the position
        where a terran building has to land to connect to addon """
        return self.position.offset(Point2((-2.5, 0.5)))

    @property_immutable_cache
    def has_add_on(self) -> bool:
        return not self.add_on_tag

    @property_immutable_cache
    def assigned_harvesters(self) -> int:
        """ Number of workers currently gathering resources at a geyser or mining base."""
        return self._proto.assigned_harvesters

    @property_immutable_cache
    def ideal_harvesters(self) -> int:
        """ Returns 3 for geysers, 2*n for n mineral patches on that base."""
        return self._proto.ideal_harvesters

    @property_immutable_cache
    def surplus_harvesters(self) -> int:
        """ Returns a positive number if it has too many harvesters mining,
        a negative number if it has too few mining """
        return self._proto.assigned_harvesters - self._proto.ideal_harvesters

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
        """ Target can be a Unit or Point2 """
        return self(AbilityId.ATTACK, *args, **kwargs)

    def gather(self, *args, **kwargs):
        """ Target can be a mineral patch or geyser """
        return self(AbilityId.HARVEST_GATHER, *args, **kwargs)

    def return_resource(self, *args, **kwargs):
        """ Does not need a target """
        return self(AbilityId.HARVEST_RETURN, *args, **kwargs)

    def move(self, *args, **kwargs):
        """ Target can be a Unit (to follow that unit) or Point2 """
        return self(AbilityId.MOVE, *args, **kwargs)

    def scan_move(self, *args, **kwargs):
        """ TODO: What does this actually do? """
        return self(AbilityId.SCAN_MOVE, *args, **kwargs)

    def hold_position(self, *args, **kwargs):
        return self(AbilityId.HOLDPOSITION, *args, **kwargs)

    def stop(self, *args, **kwargs):
        return self(AbilityId.STOP, *args, **kwargs)

    def patrol(self, *args, **kwargs):
        return self(AbilityId.PATROL, *args, **kwargs)

    def repair(self, *args, **kwargs):
        return self(AbilityId.EFFECT_REPAIR, *args, **kwargs)

    def __hash__(self):
        return hash(self.tag)

    def __call__(self, ability, *args, **kwargs):
        return unit_command.UnitCommand(ability, self, *args, **kwargs)


class UnitOrder:
    @classmethod
    def from_proto(cls, proto, game_data):
        return cls(
            game_data.abilities[proto.ability_id],
            (proto.target_world_space_pos if proto.HasField("target_world_space_pos") else proto.target_unit_tag),
            proto.progress,
        )

    def __init__(self, ability, target, progress=None):
        self.ability = ability
        self.target = target
        self.progress = progress

    def __repr__(self):
        return f"UnitOrder({self.ability}, {self.target}, {self.progress})"

