import websockets

import logging
logger = logging.getLogger(__name__)

from s2clientprotocol import sc2api_pb2 as sc_pb

from .data import Status
from .player import Computer

class ProtocolError(Exception):
    pass

class ConnectionAlreadyClosed(ProtocolError):
    pass

class Protocol(object):
    def __init__(self, ws):
        assert ws
        self._ws = ws
        self._status = None

    async def __request(self, request):
        logger.debug(f"Sending request: {request !r}")
        try:
            await self._ws.send(request.SerializeToString())
        except websockets.exceptions.ConnectionClosed:
            logger.exception("Cannot send: Connection already closed.")
            raise ConnectionAlreadyClosed("Connection already closed.")
        logger.debug(f"Request sent")

        response = sc_pb.Response()
        try:
            response_bytes = await self._ws.recv()
        except websockets.exceptions.ConnectionClosed:
            logger.exception("Cannot receive: Connection already closed.")
            raise ConnectionAlreadyClosed("Connection already closed.")
        response.ParseFromString(response_bytes)
        logger.debug(f"Response received")
        return response

    async def _execute(self, **kwargs):
        assert len(kwargs) == 1, "Only one request allowed"

        request = sc_pb.Request(**kwargs)

        response = await self.__request(request)

        new_status = Status(response.status)
        if new_status != self._status:
            logger.info(f"Client status changed to {new_status} (was {self._status})")
        self._status = new_status

        if response.error:
            logger.debug(f"Response contained an error: {response.error}")
            raise ProtocolError(f"{response.error}")

        return response

    async def ping(self):
        result = await self._execute(ping=sc_pb.RequestPing())
        return result

    async def quit(self):
        try:
            await self._execute(quit=sc_pb.RequestQuit())
        except websockets.exceptions.ConnectionClosed:
            pass
