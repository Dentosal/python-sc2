import enum
from s2clientprotocol import sc2api_pb2 as sc_pb
from s2clientprotocol import error_pb2 as error_pb

PlayerType = enum.Enum("PlayerType", sc_pb.PlayerType.items())
Race = enum.Enum("Race", sc_pb.Race.items())
Difficulty = enum.Enum("Difficulty", sc_pb.Difficulty.items())
Status = enum.Enum("Status", sc_pb.Status.items())
Result = enum.Enum("Result", sc_pb.Result.items())
Alert = enum.Enum("Alert", sc_pb.Status.items())

ActionResult = enum.Enum("ActionResult", error_pb.ActionResult.items())
