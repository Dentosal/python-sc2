#!/usr/bin/python

import asyncio
from vectors import Vector

from .sc2process import SC2Process
from .client import Client
from .player import Human, Bot, Observer
from .action import combine_actions
from .data import Race, Difficulty, Result
from .game_state import GameState


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
            start_locations = [Vector(p.x, p.y, 0) for p in game_info.start_raw.start_locations]

            for bot in bots:
                bot.ai.on_start(start_locations)

            iteration = 0
            while True:
                state = await client.observation()

                if len(state.observation.player_result) > 0:
                    return Result(min(state.observation.player_result, key=lambda p: p.player_id).result)

                gs = GameState(state.observation, game_data)

                if bots:
                    r = await client.actions(
                        combine_actions(bots[0].ai.on_step(gs, iteration), game_data)
                    )

                await client.step()
                iteration += 1

            await client.quit()

    result = asyncio.get_event_loop().run_until_complete(run())
    print(result)
