from s2clientprotocol import (
    sc2api_pb2 as sc_pb,
    common_pb2 as common_pb,
    query_pb2 as query_pb,
    debug_pb2 as debug_pb
)

import logging

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

logger = logging.getLogger(__name__)

from .cache import method_cache_forever

from .protocol import Protocol, ProtocolError
from .game_info import GameInfo
from .game_data import GameData, AbilityData
from .data import Status, Result
from .data import Race, ActionResult, ChatChannel
from .action import combine_actions
from .position import Point2, Point3
from .unit import Unit


class Client(Protocol):
    def __init__(self, ws):
        super().__init__(ws)
        self._player_id = None
        self._game_result = None
        self._debug_texts = list()
        self._debug_lines = list()
        self._debug_boxes = list()
        self._debug_spheres = list()

    @property
    def in_game(self):
        return self._status == Status.in_game

    async def join_game(self, race=None, observed_player_id=None, portconfig=None):
        ifopts = sc_pb.InterfaceOptions(raw=True)

        if race is None:
            assert isinstance(observed_player_id, int)
            # join as observer
            req = sc_pb.RequestJoinGame(
                observed_player_id=observed_player_id,
                options=ifopts
            )
        else:
            assert isinstance(race, Race)
            req = sc_pb.RequestJoinGame(
                race=race.value,
                options=ifopts
            )

        if portconfig:
            req.shared_port = portconfig.shared
            req.server_ports.game_port = portconfig.server[0]
            req.server_ports.base_port = portconfig.server[1]

            for ppc in portconfig.players:
                p = req.client_ports.add()
                p.game_port = ppc[0]
                p.base_port = ppc[1]

        result = await self._execute(join_game=req)
        self._game_result = None
        self._player_id = result.join_game.player_id
        return result.join_game.player_id

    async def leave(self):
        is_resign = self._game_result is None

        if is_resign:
            # For all clients that can leave, result of leaving the game either
            # loss, or the client will ignore the result
            self._game_result = {self._player_id: Result.Defeat}

        try:
            await self._execute(leave_game=sc_pb.RequestLeaveGame())
        except ProtocolError:
            if is_resign:
                raise

    async def save_replay(self, path):
        logger.debug(f"Requesting replay from server")
        result = await self._execute(save_replay=sc_pb.RequestSaveReplay())
        with open(path, "wb") as f:
            f.write(result.save_replay.data)
        logger.info(f"Saved replay to {path}")

    async def observation(self):
        result = await self._execute(observation=sc_pb.RequestObservation())
        if (not self.in_game) or len(result.observation.player_result) > 0:
            # Sometimes game ends one step before results are available
            if len(result.observation.player_result) == 0:
                result = await self._execute(observation=sc_pb.RequestObservation())
                assert len(result.observation.player_result) > 0

            player_id_to_result = {}
            for pr in result.observation.player_result:
                player_id_to_result[pr.player_id] = Result(pr.result)
            self._game_result = player_id_to_result
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

    async def query_pathing(self, start, end):
        assert isinstance(start, (Point2, Unit))
        assert isinstance(end, Point2)
        if isinstance(start, Point2):
            result = await self._execute(query=query_pb.RequestQuery(
                pathing=[query_pb.RequestQueryPathing(
                    start_pos=common_pb.Point2D(x=start.x, y=start.y),
                    end_pos=common_pb.Point2D(x=end.x, y=end.y)
                )]
            ))
        else:
            result = await self._execute(query=query_pb.RequestQuery(
                pathing=[query_pb.RequestQueryPathing(
                    unit_tag=start.tag,
                    end_pos=common_pb.Point2D(x=end.x, y=end.y)
                )]
            ))
        distance = float(result.query.pathing[0].distance)
        if distance <= 0.0:
            return None
        return distance

    async def query_building_placement(self, ability, positions, ignore_resources=True):
        assert isinstance(ability, AbilityData)
        result = await self._execute(query=query_pb.RequestQuery(
            placements=[query_pb.RequestQueryBuildingPlacement(
                ability_id=ability.id.value,
                target_pos=common_pb.Point2D(x=position.x, y=position.y)
            ) for position in positions],
            ignore_resource_requirements=ignore_resources
        ))
        return [ActionResult(p.result) for p in result.query.placements]

    async def query_available_abilities(self, units, ignore_resource_requirements=False):
        if not isinstance(units, list):
            assert isinstance(units, Unit)
            units = [units]
        assert len(units) > 0
        result = await self._execute(query=query_pb.RequestQuery(
            abilities=[query_pb.RequestQueryAvailableAbilities(
                unit_tag=unit.tag) for unit in units],
            ignore_resource_requirements=ignore_resource_requirements)
        )
        return [[AbilityId(a.ability_id) for a in b.abilities] for b in result.query.abilities]

    async def chat_send(self, message, team_only):
        ch = ChatChannel.Team if team_only else ChatChannel.Broadcast
        r = await self._execute(action=sc_pb.RequestAction(
            actions=[sc_pb.Action(action_chat=sc_pb.ActionChat(
                channel=ch.value,
                message=message
            ))]
        ))

    async def debug_text(self, texts, positions, color=(0, 255, 0), size_px=16):
        if isinstance(positions, list):
            if not positions:
                return

            if isinstance(texts, str):
                texts = [texts] * len(positions)
            assert len(texts) == len(positions)

            await self._execute(debug=sc_pb.RequestDebug(
                debug=[debug_pb.DebugCommand(draw=debug_pb.DebugDraw(
                    text=[debug_pb.DebugText(
                        text=t,
                        color=debug_pb.Color(r=color[0], g=color[1], b=color[2]),
                        world_pos=common_pb.Point(x=p.x, y=p.y, z=getattr(p, "z", 10)),
                        size=size_px
                    ) for t, p in zip(texts, positions)]
                ))]
            ))
        else:
            await self.debug_text([texts], [positions], color)

    def debug_text_simple(self, text, color=None):
        self._debug_texts.append(to_debug_message(text, color))

    def debug_text_2d(self, text, pos, color=None, size=8):
        self._debug_texts.append(to_debug_message(text, color, pos, False, size))

    def debug_text_3d(self, text, pos, color=None, size=8):
        self._debug_texts.append(to_debug_message(text, color, pos, True, size))

    def debug_line_out(self, p0, p1, color=None):
        self._debug_lines.append(debug_pb.DebugLine(
            line=debug_pb.Line(p0=to_debug_point(p0), p1=to_debug_point(p1)),
            color=to_debug_color(color)))

    def debug_box_out(self, p_min, p_max, color=None):
        self._debug_boxes.append(debug_pb.DebugBox(
            min=to_debug_point(p_min),
            max=to_debug_point(p_max),
            color=to_debug_color(color)
        ))
		
    def debug_sphere_out(self, p, r, color=None):
        self._debug_spheres.append(debug_pb.DebugSphere(
            p=to_debug_point(p),
            r=r,
            color=to_debug_color(color)
        ))

    async def send_debug(self):
		await self._execute(debug=sc_pb.RequestDebug(
            debug=[debug_pb.DebugCommand(draw=debug_pb.DebugDraw(
                text=self._debug_texts if len(self._debug_texts) > 0 else None,
                lines=self._debug_lines if len(self._debug_lines) > 0 else None,
                boxes=self._debug_boxes if len(self._debug_boxes) > 0 else None,
                spheres=self._debug_spheres if len(self._debug_spheres) > 0 else None
            ))]

        ))
        self._debug_texts.clear()
        self._debug_lines.clear()
        self._debug_boxes.clear()
        self._debug_spheres.clear()
		
	async def debug_create_unit(self, unit_type, amount_of_units, position, owner_id):
        # example:
        # await self._client.debug_create_unit(MARINE, 1, self._game_info.map_center, 1)
        assert isinstance(unit_type, UnitTypeId)
        assert 0 < amount_of_units # careful, in realtime=True mode, as of now units get created the double amount
        assert isinstance(position, (Point2, Point3))
        assert 1 <= owner_id <= 2

        await self._execute(debug=sc_pb.RequestDebug(
            debug=[debug_pb.DebugCommand(create_unit=debug_pb.DebugCreateUnit(
                unit_type=unit_type.value,
                owner=owner_id,
                pos=common_pb.Point2D(x=position.x, y=position.y),
                quantity=(amount_of_units)
            ))]
        ))
		
    

def to_debug_color(color):
    if color is None:
        return debug_pb.Color(r=255, g=255, b=255)
    else:
        r = getattr(color, "r", getattr(color, "x", 255))
        g = getattr(color, "g", getattr(color, "y", 255))
        b = getattr(color, "b", getattr(color, "z", 255))
        if r + g + b <= 3:
            r *= 255
            g *= 255
            b *= 255

        return debug_pb.Color(r=int(r), g=int(g), b=int(b))


def to_debug_point(point):
    return common_pb.Point(x=point.x, y=point.y, z=getattr(point, "z", 0))


def to_debug_message(text, color=None, pos=None, is3d=False, size=8):
    text = text
    color = to_debug_color(color)
    size = size
    pt3d = None
    virtual_pos = None

    if pos is not None:
        if is3d:
            pt3d = to_debug_point(pos)
        else:
            virtual_pos = to_debug_point(pos)
    return debug_pb.DebugText(
        color=color,
        text=text,
        virtual_pos=virtual_pos,
        world_pos=pt3d,
        size=size
    )
