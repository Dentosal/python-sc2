import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import sc2
from sc2 import Race
from sc2.player import Bot

from sc2.units import Units
from sc2.unit import Unit
from sc2.position import Point2, Point3

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.buff_id import BuffId
from sc2.ids.ability_id import AbilityId

from sc2.player import Bot, Computer
from sc2.data import Difficulty

from sc2.game_data import GameData
from sc2.game_info import GameInfo
from sc2.game_state import GameState

from sc2.protocol import ProtocolError

from typing import List, Dict, Set, Tuple, Any, Optional, Union

from s2clientprotocol import sc2api_pb2 as sc_pb
import pickle, os, sys, logging, traceback


"""
This "bot" will loop over several available ladder maps and generate the pickle file in the "/test/pickle_data/" subfolder.
These will then be used to run tests from the test script "test_pickled_data.py"
"""

class ExporterBot(sc2.BotAI):
    async def on_step(self, iteration):
        if iteration == 0:
            await self.on_first_iteration()

        actions = []
        await self.do_actions(actions)

    async def on_start_async(self):
        raw_game_data = await self._client._execute(
            data=sc_pb.RequestData(ability_id=True, unit_type_id=True, upgrade_id=True, buff_id=True, effect_id=True)
        )

        raw_game_info = await self._client._execute(game_info=sc_pb.RequestGameInfo())

        raw_observation = self.state.response_observation

        # To test if this data is convertable in the first place
        game_data = GameData(raw_game_data.data)
        game_info = GameInfo(raw_game_info.game_info)
        game_state = GameState(raw_observation)

        map_name = self.game_info.map_name
        print(f"Saving file to {map_name}.pkl")
        folder_path = os.path.dirname(__file__)
        subfolder_name = "pickle_data"
        file_name = f"{map_name}.pkl"
        file_path = os.path.join(folder_path, subfolder_name, file_name)
        try:
            os.makedirs(os.path.dirname(file_path))
        except:
            pass
        with open(file_path, "wb") as f:
            pickle.dump([raw_game_data, raw_game_info, raw_observation], f)

        await self._client.leave()


def main():

    maps = [
        "Acropolis",
        "Artana",
        "CrystalCavern",
        "DigitalFrontier",
        "OldSunshine",
        "Treachery",
        "Triton",
        "AutomatonLE",
        "BlueshiftLE",
        "CeruleanFallLE",
        "DarknessSanctuaryLE",
        "KairosJunctionLE",
        "ParaSiteLE",
        "PortAleksanderLE",
        "Bandwidth",
        "Ephemeron",
        "PrimusQ9",
        "Reminiscence",
        "Sanglune",
        "TheTimelessVoid",
        "Urzagol",
    ]

    for map in maps:
        logger = logging.getLogger()
        try:
            sc2.run_game(
                sc2.maps.get(map),
                [Bot(Race.Terran, ExporterBot()), Computer(Race.Zerg, Difficulty.Easy)],
                realtime=False,
                save_replay_as="Example.SC2Replay",
            )
        except ProtocolError:
            # ProtocolError appears after a leave game request
            pass
        except Exception as e:
            logger.warning(f"Map {map} could not be found, so pickle files for that map could not be generated. Error: {e}")
            # traceback.print_exc()


if __name__ == "__main__":
    main()
