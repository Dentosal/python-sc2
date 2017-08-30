import enum
from s2clientprotocol import (
    sc2api_pb2 as sc_pb,
    raw_pb2 as raw_pb,
    data_pb2 as data_pb,
    error_pb2 as error_pb
)
from .ids.unit_typeid import PROBE, SCV, DRONE

PlayerType = enum.Enum("PlayerType", sc_pb.PlayerType.items())
Race = enum.Enum("Race", sc_pb.Race.items())
Difficulty = enum.Enum("Difficulty", sc_pb.Difficulty.items())
Status = enum.Enum("Status", sc_pb.Status.items())
Result = enum.Enum("Result", sc_pb.Result.items())
Alert = enum.Enum("Alert", sc_pb.Alert.items())
ChatChannel = enum.Enum("ChatChannel", sc_pb.ActionChat.Channel.items())

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
