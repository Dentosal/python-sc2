import enum
from s2clientprotocol import (
    sc2api_pb2 as sc_pb,
    raw_pb2 as raw_pb,
    data_pb2 as data_pb,
    common_pb2 as common_pb,
    error_pb2 as error_pb
)
from .ids.unit_typeid import PROBE, SCV, DRONE
from .ids.unit_typeid import NEXUS
from .ids.unit_typeid import COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS
from .ids.unit_typeid import HATCHERY, LAIR, HIVE
from .ids.unit_typeid import ASSIMILATOR, REFINERY, EXTRACTOR

from .ids.ability_id import TRAIN_ZEALOT, TRAIN_STALKER, TRAIN_HIGHTEMPLAR, TRAIN_DARKTEMPLAR, TRAIN_SENTRY, \
    TRAIN_ADEPT
from .ids.ability_id import \
    TRAINWARP_ZEALOT, \
    TRAINWARP_STALKER, \
    TRAINWARP_HIGHTEMPLAR, \
    TRAINWARP_DARKTEMPLAR, \
    TRAINWARP_SENTRY, \
    TRAINWARP_ADEPT

PlayerType = enum.Enum("PlayerType", sc_pb.PlayerType.items())
Difficulty = enum.Enum("Difficulty", sc_pb.Difficulty.items())
Status = enum.Enum("Status", sc_pb.Status.items())
Result = enum.Enum("Result", sc_pb.Result.items())
Alert = enum.Enum("Alert", sc_pb.Alert.items())
ChatChannel = enum.Enum("ChatChannel", sc_pb.ActionChat.Channel.items())

Race = enum.Enum("Race", common_pb.Race.items())

DisplayType = enum.Enum("DisplayType", raw_pb.DisplayType.items())
Alliance = enum.Enum("Alliance", raw_pb.Alliance.items())
CloakState = enum.Enum("CloakState", raw_pb.CloakState.items())

Attribute = enum.Enum("Attribute", data_pb.Attribute.items())

ActionResult = enum.Enum("ActionResult", error_pb.ActionResult.items())

race_worker = {
    Race.Protoss: PROBE,
    Race.Terran: SCV,
    Race.Zerg: DRONE
}

race_townhalls = {
    Race.Protoss: {NEXUS},
    Race.Terran: {COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS},
    Race.Zerg: {HATCHERY, LAIR, HIVE}
}

warpgate_abilities = {
    TRAIN_ZEALOT: TRAINWARP_ZEALOT,
    TRAIN_STALKER: TRAINWARP_STALKER,
    TRAIN_HIGHTEMPLAR: TRAINWARP_HIGHTEMPLAR,
    TRAIN_DARKTEMPLAR: TRAINWARP_DARKTEMPLAR,
    TRAIN_SENTRY: TRAINWARP_SENTRY,
    TRAIN_ADEPT: TRAINWARP_ADEPT
}

race_gas = {
    Race.Protoss: ASSIMILATOR,
    Race.Terran: REFINERY,
    Race.Zerg: EXTRACTOR
}
