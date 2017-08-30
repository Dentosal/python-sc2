from itertools import groupby
from s2clientprotocol import raw_pb2 as raw_pb, common_pb2 as common_pb

from .position import Point2
from .unit import Unit
from .ids.ability_id import AbilityId

def combine_actions(action_iter, game_data):
    for key, items in groupby(action_iter, key=lambda a: a.combining_tuple):
        ability, target, queue = key

        if target is None:
            cmd = raw_pb.ActionRawUnitCommand(
                ability_id=ability.value,
                unit_tags=[u.unit.tag for u in items],
                queue_command=queue
            )
        elif isinstance(target, Point2):
            cmd = raw_pb.ActionRawUnitCommand(
                ability_id=ability.value,
                unit_tags=[u.unit.tag for u in items],
                queue_command=queue,
                target_world_space_pos=common_pb.Point2D(x=target.x, y=target.y)
            )
        elif isinstance(target, Unit):
            cmd = raw_pb.ActionRawUnitCommand(
                ability_id=ability.value,
                unit_tags=[u.unit.tag for u in items],
                queue_command=queue,
                target_unit_tag=target.tag
            )
        else:
            raise RuntimeError(f"Must target an unit or a point or None, found '{target !r}'")

        yield raw_pb.ActionRaw(unit_command=cmd)


class UnitCommand(object):
    def __init__(self, ability, unit, target=None, queue=False):
        assert ability in AbilityId
        assert isinstance(unit, Unit)
        assert target is None or isinstance(target, (Point2, Unit))
        assert isinstance(queue, bool)
        self.ability = ability
        self.unit = unit
        self.target = target
        self.queue = queue

    @property
    def combining_tuple(self):
        return (self.ability, self.target, self.queue)

    def __repr__(self):
        return f"UnitCommand({self.ability}, {self.unit}, {self.target}, {self.queue})"
