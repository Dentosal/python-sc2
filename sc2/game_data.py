from .util import name_matches

class GameData(object):
    def __init__(self, data):
        self.abilities = {a.ability_id: AbilityData(a) for a in data.abilities if a.available}
        self.units = {u.unit_id: UnitTypeData(u) for u in data.units if u.available}

    def find_ability_by_name(self, name):
        for a in self.abilities.values():
            if a.matches(name):
                return a

        raise RuntimeError(f"Unknown action '{name}'")


class AbilityData(object):
    def __init__(self, proto):
        self._proto = proto

    @property
    def id(self):
        return self._proto.ability_id

    def matches(self, name):
        return any(name_matches(name, n) for n in (self._proto.button_name, self._proto.friendly_name))

    def __repr__(self):
        return f"AbilityData(name={self._proto.button_name})"

class UnitTypeData(object):
    def __init__(self, proto):
        self._proto = proto

    @property
    def name(self):
        return self._proto.name

    @property
    def attributes(self):
        return self._proto.attributes

    @property
    def cost(self):
        return Cost(
            self._proto.mineral_cost,
            self._proto.vespene_cost
        )

class Cost(object):
    def __init__(self, minerals, vespene, time=None):
        self.minerals = minerals
        self.vespene = vespene
        self.time = time
