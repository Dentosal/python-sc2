from vectors import Vector

from s2clientprotocol import sc2api_pb2 as sc_pb, raw_pb2 as raw_pb

from .data import Alliance, Attribute, DisplayType

class Unit(object):
    def __init__(self, proto_data, type_data):
        assert isinstance(proto_data, raw_pb.Unit)
        self._proto = proto_data
        self._type_data = type_data

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
    def pos(self):
        return Vector(self._proto.pos.x, self._proto.pos.y, self._proto.pos.z)

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
    def ready(self):
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

    # @property
    # def orders(self):
    #     return self._proto.orders
