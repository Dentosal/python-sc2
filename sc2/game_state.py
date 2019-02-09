from typing import Any, Dict, List, Optional, Set, Tuple, Union  # mypy type checking

from .data import Alliance, DisplayType
from .ids.effect_id import EffectId
from .ids.upgrade_id import UpgradeId
from .ids.unit_typeid import UnitTypeId
from .pixel_map import PixelMap
from .position import Point2, Point3
from .power_source import PsionicMatrix
from .score import ScoreDetails
from .units import Units
from .constants import geyser_ids, mineral_ids


class Blip:
    def __init__(self, proto):
        self._proto = proto

    @property
    def is_blip(self) -> bool:
        """Detected by sensor tower."""
        return self._proto.is_blip

    @property
    def is_snapshot(self) -> bool:
        return self._proto.display_type == DisplayType.Snapshot.value

    @property
    def is_visible(self) -> bool:
        return self._proto.display_type == DisplayType.Visible.value

    @property
    def alliance(self) -> Alliance:
        return self._proto.alliance

    @property
    def is_mine(self) -> bool:
        return self._proto.alliance == Alliance.Self.value

    @property
    def is_enemy(self) -> bool:
        return self._proto.alliance == Alliance.Enemy.value

    @property
    def position(self) -> Point2:
        """2d position of the blip."""
        return self.position3d.to2

    @property
    def position3d(self) -> Point3:
        """3d position of the blip."""
        return Point3.from_proto(self._proto.pos)


class Common:
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


class EffectData:
    def __init__(self, proto):
        self._proto = proto

    @property
    def id(self) -> EffectId:
        return EffectId(self._proto.effect_id)

    @property
    def positions(self) -> List[Point2]:
        return [Point2.from_proto(p) for p in self._proto.pos]


class GameState:
    def __init__(self, response_observation, game_data):
        self.actions = response_observation.actions  # successful actions since last loop
        self.action_errors = response_observation.action_errors  # error actions since last loop
        # https://github.com/Blizzard/s2client-proto/blob/51662231c0965eba47d5183ed0a6336d5ae6b640/s2clientprotocol/sc2api.proto#L575
        # TODO: implement alerts https://github.com/Blizzard/s2client-proto/blob/51662231c0965eba47d5183ed0a6336d5ae6b640/s2clientprotocol/sc2api.proto#L640
        self.observation = response_observation.observation
        self.observation_raw = self.observation.raw_data
        self.player_result = response_observation.player_result
        self.chat = response_observation.chat
        self.common: Common = Common(self.observation.player_common)
        self.psionic_matrix: PsionicMatrix = PsionicMatrix.from_proto(
            self.observation.raw_data.player.power_sources
        )  # what area pylon covers
        self.game_loop: int = self.observation.game_loop  # game loop, 22.4 per second on faster game speed

        self.score: ScoreDetails = ScoreDetails(
            self.observation.score
        )  # https://github.com/Blizzard/s2client-proto/blob/33f0ecf615aa06ca845ffe4739ef3133f37265a9/s2clientprotocol/score.proto#L31
        self.abilities = self.observation.abilities  # abilities of selected units

        # Fix for enemy units detected by my sensor tower, as blips have less unit information than normal visible units
        visibleUnits, hiddenUnits, minerals, geysers, destructables, enemy, own = ([] for _ in range(7))

        for unit in self.observation.raw_data.units:
            if unit.is_blip:
                hiddenUnits.append(unit)
            else:
                visibleUnits.append(unit)
                # all destructable rocks except the one below the main base ramps
                if unit.alliance == Alliance.Neutral.value and unit.radius > 1.5:
                    destructables.append(unit)
                elif unit.alliance == Alliance.Neutral.value:
                    # mineral field enums
                    if unit.unit_type in mineral_ids:
                        minerals.append(unit)
                    # geyser enums
                    elif unit.unit_type in geyser_ids:
                        geysers.append(unit)
                elif unit.alliance == Alliance.Self.value:
                    own.append(unit)
                elif unit.alliance == Alliance.Enemy.value:
                    enemy.append(unit)

        self.own_units: Units = Units.from_proto(own, game_data)
        self.enemy_units: Units = Units.from_proto(enemy, game_data)
        self.mineral_field: Units = Units.from_proto(minerals, game_data)
        self.vespene_geyser: Units = Units.from_proto(geysers, game_data)
        self.resources: Units = Units.from_proto(minerals + geysers, game_data)
        self.destructables: Units = Units.from_proto(destructables, game_data)
        self.units: Units = Units.from_proto(visibleUnits, game_data)
        self.upgrades: Set[UpgradeId] = {UpgradeId(upgrade) for upgrade in self.observation_raw.player.upgrade_ids}
        self.dead_units: Set[int] = {
            dead_unit_tag for dead_unit_tag in self.observation_raw.event.dead_units
        }  # set of unit tags that died this step - sometimes has multiple entries

        self.blips: Set[Blip] = {Blip(unit) for unit in hiddenUnits}
        self.visibility: PixelMap = PixelMap(self.observation_raw.map_state.visibility)
        self.creep: PixelMap = PixelMap(self.observation_raw.map_state.creep)

        self.effects: Set[EffectData] = {
            EffectData(effect) for effect in self.observation_raw.effects
        }  # effects like ravager bile shot, lurker attack, everything in effect_id.py
        """ Usage:
        for effect in self.state.effects:
            if effect.id == EffectId.RAVAGERCORROSIVEBILECP:
                positions = effect.positions
                # dodge the ravager biles
        """

