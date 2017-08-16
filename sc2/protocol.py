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

        # if len(repr(request)) < 200:
        #     print(">", repr(request))
        # else:
        #     print(">", repr(request)[:200]+"...")

        await self._ws.send(request.SerializeToString())

        response = sc_pb.Response()
        response_bytes = await self._ws.recv()
        response.ParseFromString(response_bytes)

        # if len(repr(response)) < 200:
        #     print("<", repr(response))
        # else:
        #     print("<", repr(response)[:200])
        #     print("...")

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

    async def quit(self):
        result = await self._execute(quit=sc_pb.RequestQuit())
        return result
