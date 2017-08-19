#!/usr/bin/python

import asyncio

from .sc2process import SC2Process
from .client import Client
from .player import Human, Bot, Observer
from .data import Race, Difficulty, Result, ActionResult
from .game_state import GameState

from . import pixel_map

def run_game(map_settings, players, observe=[], realtime=False):
    assert len(players) > 0, "Can't create a game without players"

    async def run():
        async with SC2Process() as server:
            await server.ping()

            bots = [p for p in players if isinstance(p, Bot)]
            participants = [p for p in players if isinstance(p, (Human, Bot))]

            if not participants:
                players.insert(0, Observer())

            await server.create_game(map_settings, players, realtime)

            client = Client(server._ws)

            if participants:
                assert players[0] is participants[0]
                await client.join_game(players[0].race)
            else:
                await client.join_game(observed_player_id=1)

            game_data = await client.get_game_data()
            game_info = await client.get_game_info()

            if bots:
                bots[0].ai._prepare_start(client, game_info, game_data)
                bots[0].ai.on_start()

            iteration = 0
            while True:
                state = await client.observation()

                if len(state.observation.player_result) > 0:
                    return Result(min(state.observation.player_result, key=lambda p: p.player_id).result)

                gs = GameState(state.observation, game_data)

                if bots:
                    bots[0].ai._prepare_step(gs)
                    await bots[0].ai.on_step(gs, iteration)

                await client.step()
                iteration += 1

            await client.quit()

    result = asyncio.get_event_loop().run_until_complete(run())
    print(result)
