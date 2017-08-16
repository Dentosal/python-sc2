from itertools import groupby
from vectors import Vector
from s2clientprotocol import raw_pb2 as raw_pb, common_pb2 as common

from .util import name_normalize, name_matches
from .unit import Unit

def combine_actions(action_iter, game_data):
    for key, items in groupby(action_iter, key=lambda a: a.combining_tuple):
        for a in game_data.abilities:
            if name_matches(key[0], a.button_name) or name_matches(key[0], a.friendly_name):
                ability_id = a.ability_id
                break
        else:
            raise RuntimeError(f"Unknown action '{key[0]}'")

        ability_name, target, queue = key

        if target is None:
            cmd = raw_pb.ActionRawUnitCommand(
                ability_id=ability_id,
                unit_tags=[u.unit.tag for u in items],
                queue_command=queue
            )
        elif isinstance(target, Vector):
            cmd = raw_pb.ActionRawUnitCommand(
                ability_id=ability_id,
                unit_tags=[u.unit.tag for u in items],
                queue_command=queue,
                target_world_space_pos=common.Point2D(x=target.x, y=target.y)
            )
        else:
            raise "ERROR"

        yield raw_pb.ActionRaw(unit_command=cmd)


class UnitCommand(object):
    def __init__(self, ability_name, unit, target=None, queue=False):
        assert isinstance(unit, Unit)
        assert target is None or isinstance(target, (Vector, Unit))
        assert isinstance(queue, bool)
        self.ability_name = name_normalize(ability_name)
        self.unit = unit
        self.target = target
        self.queue = queue

    @property
    def combining_tuple(self):
        return (self.ability_name, self.target, self.queue)
