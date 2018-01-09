import websockets

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

    async def _execute(self, **kwargs):
        assert len(kwargs) == 1, "Only one request allowed"
        request = sc_pb.Request(**kwargs)

        await self._ws.send(request.SerializeToString())

        response = sc_pb.Response()
        try:
            response_bytes = await self._ws.recv()
        except websockets.exceptions.ConnectionClosed:
            raise ProtocolError("Connection already closed.")
        response.ParseFromString(response_bytes)

        self._status = Status(response.status)

        if response.error:
            # if response.HasField("error_details"):
            #     raise ProtocolError(f"{response.error}: {response.error_details}")
            # else:
            raise ProtocolError(f"{response.error}")

        return response

    async def ping(self):
        result = await self._execute(ping=sc_pb.RequestPing())
        return result

    async def leave(self):
        try:
            await self._execute(leave_game=sc_pb.RequestLeaveGame())
        except websockets.exceptions.ConnectionClosed:
            pass

    async def quit(self):
        try:
            await self._execute(quit=sc_pb.RequestQuit())
        except websockets.exceptions.ConnectionClosed:
            pass
