from .units import Units
from .power_source import PsionicMatrix

class Common(object):
    ATTRIBUTES = [
        "player_id",
        "minerals", "vespene",
        "food_cap", "food_used",
        "food_army", "food_workers",
        "idle_worker_count", "army_count",
        "warp_gate_count", "larva_count"
    ]
    def __init__(self, proto):
        self._proto = proto

    def __getattr__(self, attr):
        assert attr in self.ATTRIBUTES, f"'{attr}' is not a valid attribute"
        return int(getattr(self._proto, attr))

class GameState(object):
    def __init__(self, observation, game_data):
        self.common = Common(observation.observation.player_common)
        self.units = Units.from_proto(observation.observation.raw_data.units, game_data)
        self.psionic_matrix = PsionicMatrix.from_proto(observation.observation.raw_data.player.power_sources)
        self.game_loop = observation.observation.game_loop

    @property
    def mineral_field(self):
        return self.units.mineral_field

    @property
    def vespene_geyser(self):
        return self.units.vespene_geyser
