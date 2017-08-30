# This file contains temporary fixes for issues already solved in the
# blizzard_internal branch of s2client-proto.
# These should be removed as soon as the changes are live and implemented.
#
# https://github.com/Blizzard/s2client-proto/tree/blizzard_internal
#
# NO OTHER CONTENT IS ALLOWED HERE

from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId

def creation_ability_from_unit_id(unit_id):
    name = UnitTypeId(unit_id).name # should return unprefixed name

    for ability in (f"BUILD_{name}", f"TRAIN_{name}"):
        if hasattr(AbilityId, ability):
            return getattr(AbilityId, ability)

    raise RuntimeError(f"Creation ability for '{name}' (id={unit_id}) not found")
