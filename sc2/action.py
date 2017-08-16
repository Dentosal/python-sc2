from itertools import groupby
from vectors import Vector
from s2clientprotocol import raw_pb2 as raw_pb, common_pb2 as common

from .unit import Unit

def combine_actions(action_iter, game_data):
    for key, items in groupby(action_iter, key=lambda a: a.combining_tuple):
        matches = list(a for a in game_data.abilities if key[0] in [a.button_name, a.friendly_name])
        assert matches, f"Unknown action '{key[0]}'"
        ability_id = matches[0].ability_id

        if isinstance(key[1], Vector):
            cmd = raw_pb.ActionRawUnitCommand(
                ability_id=ability_id,
                unit_tags=[u.unit.tag for u in items],
                queue_command=key[2],
                target_world_space_pos=common.Point2D(x=key[1].x, y=key[1].y)
            )
        else:
            raise "ERROR"

        yield raw_pb.ActionRaw(unit_command=cmd)


class UnitCommand(object):
    def __init__(self, ability_name, target, unit, queue=False):
        assert isinstance(target, (Vector, Unit))
        assert isinstance(unit, Unit)
        assert isinstance(queue, bool)
        self.ability_name = ability_name
        self.target = target
        self.unit = unit
        self.queue = queue

    @property
    def combining_tuple(self):
        return (self.ability_name, self.target, self.queue)

def command(name, *args, **kwargs):
    return UnitCommand(name, *args, **kwargs)
