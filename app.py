#!/usr/bin/python

import asyncio

from phyton.sc2process import SC2Process
from phyton.client import Client
from phyton.player import Participant, Computer
from phyton.data import Race, Difficulty
from phyton.paths import Paths
from phyton import maps

async def main():
    async with SC2Process() as server:
        await server.ping()

        m = maps.get()[0]
        print(f"Map: {m.name}")

        await server.create_game(m, [
            Participant(Race.Protoss),
            Computer(Race.Protoss, Difficulty.Easy)
        ])

        client = Client(server._ws)
        await client.join_game()

        while True:
            state = await client.observation()

            if len(state.observation.player_result) > 0:
                break

            await client.step()

        await client.quit()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
