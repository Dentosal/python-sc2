from .units import Units
from .power_source import PsionicMatrix
from .pixel_map import PixelMap
from .ids.upgrade_id import UpgradeId
from .ids.effect_id import EffectId

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
        self.psionic_matrix = PsionicMatrix.from_proto(observation.observation.raw_data.player.power_sources)
        self.game_loop = observation.observation.game_loop

        destructables = [x for x in observation.observation.raw_data.units if x.alliance == 3 and x.radius > 1.5] # all destructable rocks except the one below the main base ramps
        self.destructables = Units.from_proto(destructables, game_data)

        # fix for enemy units detected by my sensor tower
        visibleUnits, hiddenUnits = [], []
        for u in observation.observation.raw_data.units:
            hiddenUnits.append(u) if u.is_blip else visibleUnits.append(u)
        self.units = Units.from_proto(visibleUnits, game_data)
        # self.blips = Units.from_proto(hiddenUnits, game_data) # TODO: fix me

        self.visibility = PixelMap(observation.observation.raw_data.map_state.visibility)
        self.creep = PixelMap(observation.observation.raw_data.map_state.creep)

        self.dead_units = {dead_unit_tag for dead_unit_tag in observation.observation.raw_data.event.dead_units} # set of unit tags that died this step - sometimes has multiple entries
        self.effects = {effect for effect in observation.observation.raw_data.effects} # effects like ravager bile shot, lurker attack, everything in effect_id.py # usage: if RAVAGERCORROSIVEBILECP.value in self.state.effects: do stuff
        self.upgrades = {UpgradeId(upgrade) for upgrade in observation.observation.raw_data.player.upgrade_ids} # usage: if TERRANINFANTRYWEAPONSLEVEL1 in self.state.upgrades: do stuff

    @property
    def mineral_field(self):
        return self.units.mineral_field

    @property
    def vespene_geyser(self):
        return self.units.vespene_geyser
