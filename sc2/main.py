import asyncio

from .sc2process import SC2Process
from .portconfig import Portconfig
from .client import Client
from .player import Human, Bot, Observer
from .data import Race, Difficulty, Result, ActionResult
from .game_state import GameState

async def _play_game_human(client, realtime):
    while True:
        state = await client.observation()

        if len(state.observation.player_result) > 0:
            result = Result(min(state.observation.player_result, key=lambda p: p.player_id).result)
            await client.leave()
            await client.quit()
            return result

        if not realtime:
            await client.step()

async def _play_game_ai(client, player_id, ai, realtime):
    game_data = await client.get_game_data()
    game_info = await client.get_game_info()

    ai._prepare_start(client, player_id, game_info, game_data)
    ai.on_start()

    iteration = 0
    while True:
        state = await client.observation()
        if len(state.observation.player_result) > 0:
            print("OBSR", state.observation.player_result)
            result = Result(min(state.observation.player_result, key=lambda p: p.player_id).result)
            await client.leave()
            await client.quit()
            return result

        gs = GameState(state.observation, game_data)

        ai._prepare_step(gs)
        await ai.on_step(gs, iteration)

        if not realtime:
            await client.step()
        iteration += 1

async def _host_game(map_settings, players, realtime=False, observer=False, portconfig=None):
    assert len(players) > 0, "Can't create a game without players"

    if observer:
        players.append(Observer())
    else:
        assert any(isinstance(p, (Human, Bot)) for p in players)

    async with SC2Process() as server:
        await server.ping()

        await server.create_game(map_settings, players, realtime)

        client = Client(server._ws)

        if observer:
            await client.join_game(observed_player_id=1, portconfig=portconfig)
            return await _play_game_human(client, realtime)


        player_id = await client.join_game(players[0].race, portconfig=portconfig)

        if isinstance(players[0], Human):
            return await _play_game_human(client, realtime)
        else:
            return await _play_game_ai(client, player_id, players[0].ai, realtime)

async def _join_game(map_settings, players, realtime, portconfig):
    async with SC2Process() as server:
        await server.ping()
        client = Client(server._ws)

        player_id = await client.join_game(players[1].race, portconfig=portconfig)
        if isinstance(player_id, Human):
            return await _play_game_human(client, realtime)
        else:
            return await _play_game_ai(client, player_id, players[1].ai, realtime)

def run_game(*args, **kwargs):
    if sum(isinstance(p, (Human, Bot)) for p in args[1]) > 1:
        portconfig = Portconfig()
        result = asyncio.get_event_loop().run_until_complete(asyncio.gather(
            _host_game(*args, **kwargs, portconfig=portconfig),
            _join_game(*args, kwargs.get("realtime", False), portconfig)
        ))
    else:
        result = asyncio.get_event_loop().run_until_complete(_host_game(*args, **kwargs))
    print(result)
