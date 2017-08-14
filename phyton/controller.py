from s2clientprotocol import sc2api_pb2 as sc_pb
from .protocol import Protocol

class Controller(Protocol):
    def __init__(self, ws):
        super().__init__(ws)

    async def create_game(self, map_name, players):
        req = self._create_game_req(map_name, players)
        result = await self._send_recv(req)
        return result
