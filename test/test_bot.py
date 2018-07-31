import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

from sc2.position import Point2, Point3
from sc2.units import Units
from sc2.unit import Unit

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.effect_id import EffectId


class TestBot(sc2.BotAI):
    def __init__(self):
        self.tests_target = 3
        self.tests_completed = 0
        print("Test bot initialized")


    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("(glhf)")
        if iteration == 1:
            assert len(self.state.chat) >= 1, self.state.chat

        # Tests at start:
        if iteration == 5:
            # No need to use try except as the travis test script checks for "Traceback "
            # try:
            await self.test_botai_properties()
            await self.test_gamestate_static_variables()
            await self.test_game_info_static_variables()
            # except AssertionError as e:
            #     print("Assertion error: {}".format(e))
            #     exit(1000)

        """
        TODO tests:
        expansion locations, expand now, get next expnasion, distribute workers, owned expansions, can cast, select build worker, can place, find placement, already_pending, self build, do actions, chat send
        """

        # End when all tests successful
        if self.tests_completed >= self.tests_target:
            exit(0)


    # Test BotAI properties
    async def test_botai_properties(self):
        assert 1 <= self.player_id <= 2, self.player_id
        assert self.race == Race.Terran, self.race

        assert 0 <= self.time <= 180, self.time
        assert self.start_location == self.townhalls.random.position, (self.start_location, self.townhalls.random.position)
        for loc in self.enemy_start_locations:
            assert isinstance(loc, Point2), loc
            assert loc.distance_to(self.start_location) > 20, (loc, self.start_location)
        assert self.known_enemy_units.amount == 0, self.known_enemy_units
        assert self.known_enemy_structures.amount == 0, self.known_enemy_structures
        assert self.known_enemy_structures.amount <= self.known_enemy_units.amount
        assert self.main_base_ramp.top_center.distance_to(self.start_location) < 30, self.main_base_ramp.top_center
        assert len(await self.get_available_abilities(self.workers)) == self.workers.amount
        # assert self.can_afford(UnitTypeId.SCV) == True, self.minerals why error
        assert self.minerals >= 50, self.minerals
        assert self.vespene == 0, self.vespene
        assert self.supply_used == 12, self.supply_used
        assert self.supply_cap == 15, self.supply_cap
        assert self.supply_left == 3, self.supply_left

        self.tests_completed += 1


    # Test self.state variables
    async def test_gamestate_static_variables(self):
        assert len(self.state.actions) == 0, self.state.actions
        assert len(self.state.action_errors) == 0, self.state.action_errors
        assert len(self.state.chat) == 0, self.state.chat
        assert self.state.game_loop > 0, self.state.game_loop
        assert self.state.score.collection_rate_minerals >= 0, self.state.score.collection_rate_minerals
        assert len(self.state.destructables) > 0, self.state.destructables
        assert self.state.units.amount > 0, self.state.units
        assert len(self.state.blips) == 0, self.state.blips
        assert len(self.state.upgrades) == 0, self.state.upgrades
        # TODO: actions, actionerrors, observation, chat, common, psionic matrix as protoss, score, abilities, blips, pixelmaps, dead units, effects, upgrades

        self.tests_completed += 1


    # Test self._game_info variables
    async def test_game_info_static_variables(self):
        assert len(self._game_info.players) == 2, self._game_info.players
        assert len(self._game_info.map_ramps) >= 2, self._game_info.map_ramps
        assert len(self._game_info.player_races) == 2, self._game_info.player_races
        # TODO: map size, pixel maps, playable area, player races, start locations, map center

        self.tests_completed += 1

    # TODO:
    # Test position.py
    # Test unit.py
    # Test units.py
    # Test ramp building placement position




def main():
    sc2.run_game(sc2.maps.get("(2)CatalystLE"), [
        Bot(Race.Terran, TestBot()),
        Computer(Race.Zerg, Difficulty.Easy)
    ], realtime=False)

if __name__ == '__main__':
    main()
