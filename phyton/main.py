#!/usr/bin/python

import asyncio

from .sc2process import SC2Process
from .client import Client
from .data import Race, Difficulty
from .paths import Paths

def run_game(map_settings, players):
    async def run():
        async with SC2Process() as server:
            await server.ping()

            await server.create_game(map_settings, players)

            client = Client(server._ws)
            await client.join_game()

            while True:
                state = await client.observation()

                if len(state.observation.player_result) > 0:
                    break

                await client.step()

            await client.quit()

    asyncio.get_event_loop().run_until_complete(run())
