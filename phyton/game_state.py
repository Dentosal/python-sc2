from .unit import Unit

class Common(object):
    """
        Attributes:
            player_id,
            minerals, vespene,
            food_cap,
            food_used, food_army, food_workers,
            idle_worker_count, army_count,
            warp_gate_count, larva_count
    """
    def __init__(self, proto):
        self._proto = proto

    def __getattr__(self, attr):
        return int(getattr(self._proto, attr))

class GameState(object):
    def __init__(self, observation, game_data):
        self.common = Common(observation.observation.player_common)
        self.units = [
            Unit(u, game_data.units[u.unit_type])
            for u in observation.observation.raw_data.units
        ]
