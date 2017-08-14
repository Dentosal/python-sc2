import websockets
from s2clientprotocol import sc2api_pb2 as sc_pb

from .paths import Paths
from .protocol import Protocol
from .data import Race

class Client(Protocol):
    def __init__(self, ws):
        super().__init__(ws)

    async def join_game(self):
        req = self._join_game_req(Race.Protoss)
        result = await self._send_recv(req)
        return result

    async def observation(self):
        req = sc_pb.Request(observation=sc_pb.RequestObservation())
        result = await self._send_recv(req)
        return result

    async def step(self):
        req = sc_pb.Request(step=sc_pb.RequestStep(count=8))
        result = await self._send_recv(req)
        return result
