import asyncio
import async_timeout

import logging
logger = logging.getLogger(__name__)

from .sc2process import SC2Process
from .portconfig import Portconfig
from .client import Client
from .player import Human, Bot
from .data import Race, Difficulty, Result, ActionResult
from .game_state import GameState
from .protocol import ConnectionAlreadyClosed

async def _play_game_human(client, player_id, realtime):
    while True:
        state = await client.observation()
        if client._game_result:
            return client._game_result[player_id]

        if not realtime:
            await client.step()

async def _play_game_ai(client, player_id, ai, realtime, step_time_limit):
    game_data = await client.get_game_data()
    game_info = await client.get_game_info()

    ai._prepare_start(client, player_id, game_info, game_data)
    ai.on_start()

    iteration = 0
    while True:
        state = await client.observation()
        if client._game_result:
            return client._game_result[player_id]

        gs = GameState(state.observation, game_data)

        ai._prepare_step(gs)
        if realtime:
            logger.debug(f"Running AI step, realtime")
            await ai.on_step(iteration)
            logger.debug(f"Running AI step: done")
        else:
            logger.debug(f"Running AI step, timeout={step_time_limit}")
            try:
                async with async_timeout.timeout(step_time_limit):
                    await ai.on_step(iteration)
            except asyncio.TimeoutError:
                logger.error(f"Running AI step: out of time")
            logger.debug(f"Running AI step: done")

            if not client.in_game: # Client left (resigned) the game
                return client._game_result[player_id]

            await client.step()

        iteration += 1

async def _play_game(player, client, realtime, portconfig, step_time_limit=None):
    assert isinstance(realtime, bool), repr(realtime)

    player_id = await client.join_game(player.race, portconfig=portconfig)
    logging.info(f"Player id: {player_id}")

    if isinstance(player, Human):
        result = await _play_game_human(client, player_id, realtime)
    else:
        result = await _play_game_ai(client, player_id, player.ai, realtime, step_time_limit)

    logging.info(f"Result for player id: {player_id}: {result}")
    return result

async def _host_game(map_settings, players, realtime, portconfig=None, save_replay_as=None, step_time_limit=None):
    assert len(players) > 0, "Can't create a game without players"

    assert any(isinstance(p, (Human, Bot)) for p in players)

    async with SC2Process() as server:
        await server.ping()

        await server.create_game(map_settings, players, realtime)

        client = Client(server._ws)

        try:
            result = await _play_game(players[0], client, realtime, portconfig, step_time_limit)
            if save_replay_as is not None:
                await client.save_replay(save_replay_as)
            await client.leave()
            await client.quit()
        except ConnectionAlreadyClosed:
            logging.error(f"Connection was closed before the game ended")
            return None

        return result

async def _join_game(players, realtime, portconfig, save_replay_as=None, step_time_limit=None):
    async with SC2Process() as server:
        await server.ping()
        client = Client(server._ws)

        try:
            result = await _play_game(players[1], client, realtime, portconfig, step_time_limit)
            if save_replay_as is not None:
                await client.save_replay(save_replay_as)
            await client.leave()
            await client.quit()
        except ConnectionAlreadyClosed:
            logging.error(f"Connection was closed before the game ended")
            return None

        return result

def run_game(map_settings, players, **kwargs):
    if sum(isinstance(p, (Human, Bot)) for p in players) > 1:
        join_kwargs = {k: v for k,v in kwargs.items() if k != "save_replay_as"}

        portconfig = Portconfig()
        result = asyncio.get_event_loop().run_until_complete(asyncio.gather(
            _host_game(map_settings, players, **kwargs, portconfig=portconfig),
            _join_game(players, **join_kwargs, portconfig=portconfig)
        ))
    else:
        result = asyncio.get_event_loop().run_until_complete(
            _host_game(map_settings, players, **kwargs)
        )
    return result
