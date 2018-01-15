import asyncio

from .sc2process import SC2Process
from .portconfig import Portconfig
from .client import Client
from .player import Human, Bot
from .data import Race, Difficulty, Result, ActionResult
from .game_state import GameState
from .protocol import ProtocolError

def _get_result(state, player_id):
    assert len(state.observation.player_result) > 0
    for pr in state.observation.player_result:
        if pr.player_id == player_id:
            return Result(pr.result)

    raise RuntimeError("No result found for player")


async def _play_game_human(client, player_id, realtime):
    while True:
        state = await client.observation()
        if len(state.observation.player_result) > 0:
            return _get_result(state, player_id)

        try:
            if not realtime:
                await client.step()
        except ProtocolError:
            state = await client.observation()
            return _get_result(state, player_id)

async def _play_game_ai(client, player_id, ai, realtime):
    game_data = await client.get_game_data()
    game_info = await client.get_game_info()

    ai._prepare_start(client, player_id, game_info, game_data)
    ai.on_start()

    iteration = 0
    while True:
        state = await client.observation()
        if len(state.observation.player_result) > 0:
            return _get_result(state, player_id)

        gs = GameState(state.observation, game_data)

        ai._prepare_step(gs)
        try:
            await ai.on_step(gs, iteration)
            if not realtime:
                await client.step()
        except ProtocolError:
            state = await client.observation()
            return _get_result(state, player_id)

        iteration += 1

async def _play_game(player, client, realtime, portconfig):
    player_id = await client.join_game(player.race, portconfig=portconfig)

    if isinstance(player, Human):
        return await _play_game_human(client, player_id, realtime)
    else:
        return await _play_game_ai(client, player_id, player.ai, realtime)

async def _host_game(map_settings, players, realtime, portconfig=None, save_replay_as=None):
    assert len(players) > 0, "Can't create a game without players"

    assert any(isinstance(p, (Human, Bot)) for p in players)

    async with SC2Process() as server:
        await server.ping()

        await server.create_game(map_settings, players, realtime)

        client = Client(server._ws)

        result = await _play_game(players[0], client, realtime, portconfig)
        if save_replay_as is not None:
            await client.save_replay(save_replay_as)
        await client.leave()
        await client.quit()
        return result

async def _join_game(players, realtime, portconfig):
    async with SC2Process() as server:
        await server.ping()
        client = Client(server._ws)

        result = await _play_game(players[1], client, realtime, portconfig)
        await client.leave()
        await client.quit()
        return result

def run_game(map_settings, players, **kwargs):
    if sum(isinstance(p, (Human, Bot)) for p in players) > 1:
        portconfig = Portconfig()
        result = asyncio.get_event_loop().run_until_complete(asyncio.gather(
            _host_game(map_settings, players, **kwargs, portconfig=portconfig),
            _join_game(players, kwargs.get("realtime", False), portconfig)
        ))
    else:
        result = asyncio.get_event_loop().run_until_complete(
            _host_game(map_settings, players, **kwargs)
        )
    return result
