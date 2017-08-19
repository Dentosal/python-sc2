from s2clientprotocol import sc2api_pb2 as sc_pb, common_pb2 as common_pb, query_pb2 as query_pb

from .cache import method_cache_forever

from .protocol import Protocol
from .game_info import GameInfo
from .game_data import GameData
from .data import Race, ActionResult
from .action import combine_actions

class Client(Protocol):
    def __init__(self, ws):
        super().__init__(ws)

    async def join_game(self, race=None, observed_player_id=None):
        if race is None:
            assert isinstance(observed_player_id, int)
            # join as observer
            req = sc_pb.RequestJoinGame(
                observed_player_id=observed_player_id,
                options=sc_pb.InterfaceOptions(raw=True)
            )
        else:
            assert isinstance(race, Race)
            req = sc_pb.RequestJoinGame(
                race=race.value,
                options=sc_pb.InterfaceOptions(raw=True)
            )
        result = await self._execute(join_game=req)
        return result

    async def observation(self):
        result = await self._execute(observation=sc_pb.RequestObservation())
        return result

    async def step(self):
        result = await self._execute(step=sc_pb.RequestStep(count=8))
        return result

    async def get_game_data(self):
        result = await self._execute(data=sc_pb.RequestData(
            ability_id=True,
            unit_type_id=True,
            upgrade_id=True
        ))
        return GameData(result.data)

    async def get_game_info(self):
        result = await self._execute(game_info=sc_pb.RequestGameInfo())
        return GameInfo(result.game_info)

    async def actions(self, actions, game_data, return_successes=False):
        if not isinstance(actions, list):
            res = await self.actions([actions], game_data, return_successes)
            if res:
                return res[0]
            else:
                return None
        else:
            actions = combine_actions(actions, game_data)

            res = await self._execute(action=sc_pb.RequestAction(
                actions=[sc_pb.Action(action_raw=a) for a in actions]
            ))

            res = [ActionResult(r) for r in res.action.result]
            if return_successes:
                return res
            else:
                return [r for r in res if r != ActionResult.Success]

    async def query_building_placement(self, ability_id, positions, ignore_resources=True):
        result = await self._execute(query=query_pb.RequestQuery(
            placements=[query_pb.RequestQueryBuildingPlacement(
                ability_id=ability_id,
                target_pos=common_pb.Point2D(x=position.x, y=position.y)
            ) for position in positions],
            ignore_resource_requirements=ignore_resources
        ))
        return [ActionResult(p.result) for p in result.query.placements]
