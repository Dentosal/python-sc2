from s2clientprotocol import sc2api_pb2 as sc_pb, raw_pb2 as raw_pb

from .position import Point3
from .util import name_matches
from .data import Alliance, Attribute, DisplayType
from .game_data import GameData
from . import action

class Unit(object):
    def __init__(self, proto_data, game_data):
        assert isinstance(proto_data, raw_pb.Unit)
        assert isinstance(game_data, GameData)
        self._proto = proto_data
        self._game_data = game_data

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
    def tag(self):
        return self._proto.tag

    @property
    def unit_type_id(self):
        return self._proto.unit_type

    @property
    def owner_id(self):
        return self._proto.owner

    @property
    def position(self):
        return Point3.from_proto(self._proto.pos)

    def distance_to(self, p):
        return self.position.to2.distance_to(p.to2)

    @property
    def facing(self):
        return self._proto.facing

    @property
    def radius(self):
        return self._proto.radius

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
    def is_burrowed(self):
        return self._proto.is_burrowed

    @property
    def is_flying(self):
        return self._proto.is_flying

    @property
    def is_structure(self):
        return Attribute.Structure.value in self._type_data.attributes

    @property
    def health(self):
        return self._proto.health

    @property
    def health_max(self):
        return self._proto.health_max

    @property
    def shield(self):
        return self._proto.shield

    @property
    def energy(self):
        return self._proto.energy

    @property
    def mineral_contents(self):
        return self._proto.mineral_contents

    @property
    def is_selected(self):
        return self._proto.is_selected

    @property
    def orders(self):
        return [UnitOrder.from_proto(o, self._game_data) for o in self._proto.orders]

    @property
    def is_idle(self):
        return not self.orders

    @property
    def name(self):
        return self._type_data.name

    def matches(self, name):
        return name_matches(self.name, name)

    def __call__(self, ability_name, *args, **kwargs):
        return action.UnitCommand(ability_name, self, *args, **kwargs)

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
