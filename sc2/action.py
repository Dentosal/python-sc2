from itertools import groupby
from s2clientprotocol import raw_pb2 as raw_pb, common_pb2 as common_pb

from .position import Point2
from .util import name_normalize
from .unit import Unit

def combine_actions(action_iter, game_data):
    for key, items in groupby(action_iter, key=lambda a: a.combining_tuple):
        ability_name, target, queue = key
        ability_id = game_data.find_ability_by_name(ability_name).id

        if target is None:
            cmd = raw_pb.ActionRawUnitCommand(
                ability_id=ability_id,
                unit_tags=[u.unit.tag for u in items],
                queue_command=queue
            )
        elif isinstance(target, Point2):
            cmd = raw_pb.ActionRawUnitCommand(
                ability_id=ability_id,
                unit_tags=[u.unit.tag for u in items],
                queue_command=queue,
                target_world_space_pos=common_pb.Point2D(x=target.x, y=target.y)
            )
        else:
            raise "ERROR"

        yield raw_pb.ActionRaw(unit_command=cmd)


class UnitCommand(object):
    def __init__(self, ability_name, unit, target=None, queue=False):
        assert isinstance(unit, Unit)
        assert target is None or isinstance(target, (Point2, Unit))
        assert isinstance(queue, bool)
        self.ability_name = name_normalize(ability_name)
        self.unit = unit
        self.target = target
        self.queue = queue

    @property
    def combining_tuple(self):
        return (self.ability_name, self.target, self.queue)
