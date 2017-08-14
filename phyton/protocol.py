from s2clientprotocol import sc2api_pb2 as sc_pb
from .data import Status
from .player import Computer

class ProtocolError(Exception):
    pass

class Protocol(object):
    def __init__(self, ws):
        assert ws
        self._ws = ws
        self._status = None

    async def _send_recv(self, req):
        # print(">", repr(req))
        await self._ws.send(req.SerializeToString())

        response = sc_pb.Response()
        response_bytes = await self._ws.recv()
        response.ParseFromString(response_bytes)

        # print("<", repr(response))

        self._status = Status(response.status)

        if response.error:
            # if response.HasField("error_details"):
            #     raise ProtocolError(f"{response.error}: {response.error_details}")
            # else:
            raise ProtocolError(f"{response.error}")

        return response


    async def ping(self):
        result = await self._send_recv(sc_pb.Request(ping=sc_pb.RequestPing()))
        return result

    async def quit(self):
        result = await self._send_recv(sc_pb.Request(quit=sc_pb.RequestQuit()))
        return result

    def _create_game_req(self, game_map, players):
        req = sc_pb.RequestCreateGame(
            local_map=sc_pb.LocalMap(
                map_path=str(game_map.path)
            )
        )

        for player in players:
            p = req.player_setup.add()
            p.type = player.type.value
            p.race = player.race.value
            if isinstance(player, Computer):
                p.difficulty = player.difficulty.value

        return sc_pb.Request(create_game=req)

    def _join_game_req(self, race):
        req = sc_pb.RequestJoinGame(
            race=race.value,
            options=sc_pb.InterfaceOptions(raw=True)
        )
        return sc_pb.Request(join_game=req)
