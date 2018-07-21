from s2clientprotocol import sc2api_pb2 as sc_pb, raw_pb2 as raw_pb
from sc2.ids.buff_id import BuffId

from .position import Point3
from .data import Alliance, Attribute, DisplayType, warpgate_abilities
from .game_data import GameData
from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId
from . import unit_command

class Unit(object):
    def __init__(self, proto_data, game_data):
        assert isinstance(proto_data, raw_pb.Unit)
        assert isinstance(game_data, GameData)
        self._proto = proto_data
        self._game_data = game_data

    @property
    def type_id(self):
        return UnitTypeId(self._proto.unit_type)

    @property
    def _type_data(self):
        return self._game_data.units[self._proto.unit_type]

    @property
    def is_snapshot(self):
        return self._proto.display_type == DisplayType.Snapshot.value

    @property
    def is_visible(self):
        return self._proto.display_type == DisplayType.Visible.value

    @property
    def alliance(self):
        return self._proto.alliance

    @property
    def is_mine(self):
        return self._proto.alliance == Alliance.Self.value

    @property
    def is_enemy(self):
        return self._proto.alliance == Alliance.Enemy.value

    @property
    def tag(self):
        return self._proto.tag

    @property
    def owner_id(self):
        return self._proto.owner

    @property
    def position(self):
        """2d position of the unit."""
        return self.position3d.to2

    @property
    def position3d(self):
        """3d position of the unit."""
        return Point3.from_proto(self._proto.pos)

    def distance_to(self, p):
        return self.position.to2.distance_to(p.position.to2)

    @property
    def facing(self):
        return self._proto.facing

    @property
    def radius(self):
        return self._proto.radius

    @property
    def detect_range(self):
        return self._proto.detect_range

    @property
    def radar_range(self):
        return self._proto.radar_range

    @property
    def build_progress(self):
        return self._proto.build_progress

    @property
    def is_ready(self):
        return self.build_progress == 1.0

    @property
    def cloak(self):
        return self._proto.cloak

    @property
    def is_blip(self):
        """Detected by sensor tower."""
        return self._proto.is_blip

    @property
    def is_powered(self):
        return self._proto.is_powered

    @property
    def is_burrowed(self):
        return self._proto.is_burrowed

    @property
    def is_flying(self):
        return self._proto.is_flying

    @property
    def is_structure(self):
        return Attribute.Structure.value in self._type_data.attributes

    @property
    def is_mineral_field(self):
        return self._type_data.has_minerals

    @property
    def is_vespene_geyser(self):
        return self._type_data.has_vespene

    @property
    def health(self):
        return self._proto.health

    @property
    def health_max(self):
        return self._proto.health_max

    @property
    def health_percentage(self):
        if self._proto.health_max == 0:
            return 0
        return self._proto.health / self._proto.health_max

    @property
    def shield(self):
        return self._proto.shield

    @property
    def shield_max(self):
        return self._proto.shield_max

    @property
    def shield_percentage(self):
        if self._proto.shield_max == 0:
            return 0
        return self._proto.shield / self._proto.shield_max

    @property
    def energy(self):
        return self._proto.energy

    @property
    def energy_max(self):
        return self._proto.energy_max

    @property
    def energy_percentage(self):
        if self._proto.energy_max == 0:
            return 0
        return self._proto.energy / self._proto.energy_max

    @property
    def mineral_contents(self):
        """ How many minerals a mineral field has left to mine from """
        return self._proto.mineral_contents

    @property
    def vespene_contents(self):
        """ How much gas is remaining in a geyser """
        return self._proto.vespene_contents

    @property
    def has_vespene(self):
        """ Checks if a geyser has gas remaining (cant build extractors on empty geysers), useful for lategame """
        return self._proto.vespene_contents > 0

    @property
    def weapon_cooldown(self):
        """ Returns time in game loops (self.state.game_loop) until the unit can fire again 
        Usage: 
        if unit.weapon_cooldown == 0:
            await self.do(unit.attack(target))
        else:
            await self.do(unit.move(retreatPosition))
        """
        if self.can_attack_ground or self.can_attack_air:
            return self._proto.weapon_cooldown
        return 1000

    @property
    def can_attack_ground(self):
        # See data_pb2.py line 141 for info on weapon data
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [1, 3]), None)
            return weapon is not None
        return False
    
    @property
    def ground_dps(self):
        """ Does not include upgrades """
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [1, 3]), None)
            if weapon:
                return (weapon.damage * weapon.attacks) / weapon.speed
        return 0

    @property
    def ground_range(self):
        """ Does not include upgrades """
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [1, 3]), None)
            if weapon:
                return weapon.range
        return 0

    @property
    def can_attack_air(self):
        """ Does not include upgrades """
        # See data_pb2.py line 141 for info on weapon data
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [2, 3]), None)
            return weapon is not None
        return False

    @property
    def air_dps(self):
        """ Does not include upgrades """
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [2, 3]), None)
            if weapon:
                return (weapon.damage * weapon.attacks) / weapon.speed
        return 0

    @property
    def air_range(self):
        """ Does not include upgrades """
        if hasattr(self._type_data._proto, "weapons"):
            weapons = self._type_data._proto.weapons
            weapon = next((weapon for weapon in weapons if weapon.type in [2, 3]), None)
            if weapon:
                return weapon.range
        return 0

    @property
    def armor(self):
        """ Does not include upgrades """
        return self._type_data._proto.armor

    @property
    def is_carrying_minerals(self):
        return self.has_buff(BuffId.CARRYMINERALFIELDMINERALS) or self.has_buff(BuffId.CARRYHIGHYIELDMINERALFIELDMINERALS)

    @property
    def is_carrying_vespene(self):
        return self.has_buff(BuffId.CARRYHARVESTABLEVESPENEGEYSERGAS) or self.has_buff(BuffId.CARRYHARVESTABLEVESPENEGEYSERGASPROTOSS) or self.has_buff(BuffId.CARRYHARVESTABLEVESPENEGEYSERGASZERG)

    @property
    def is_selected(self):
        return self._proto.is_selected

    @property
    def orders(self):
        return [UnitOrder.from_proto(o, self._game_data) for o in self._proto.orders]

    @property
    def noqueue(self):
        return len(self.orders) == 0

    @property
    def is_moving(self):
        return len(self.orders) > 0 and self.orders[0].ability.id in [AbilityId.MOVE]

    @property
    def is_attacking(self):
        return len(self.orders) > 0 and self.orders[0].ability.id in [AbilityId.ATTACK, AbilityId.ATTACK_ATTACK, AbilityId.ATTACK_ATTACKTOWARDS, AbilityId.ATTACK_ATTACKBARRAGE, AbilityId.SCAN_MOVE]

    @property
    def is_gathering(self):
        """ Checks if a unit is on its way to a mineral field / vespene geyser to mine """
        return len(self.orders) > 0 and self.orders[0].ability.id in [AbilityId.HARVEST_GATHER]

    @property
    def order_target(self):
        """ Returns the target tag (if it is a Unit) or Point2 (if it is a Position) from the first order """
        if len(self.orders) > 0:
            return self.orders[0].target
        return None

    @property
    def is_idle(self):
        return not self.orders

    @property
    def add_on_tag(self):
        return self._proto.add_on_tag

    @property
    def has_add_on(self):
        return self.add_on_tag != 0

    @property
    def assigned_harvesters(self):
        return self._proto.assigned_harvesters

    @property
    def ideal_harvesters(self):
        return self._proto.ideal_harvesters

    @property
    def surplus_harvesters(self):
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

    def __eq__(self, other):
        return self.tag == other.tag

    def __ne__(self, other):
        return self.tag != other.tag

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
