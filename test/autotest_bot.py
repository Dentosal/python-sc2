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
        # Tests related
        self.game_time_timeout_limit = 2*60
        self.tests_target = 8
        self.tests_done_by_name = set()

        # Variables handled by tests



    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("(glhf)")
        if iteration == 1:
            # Test if chat message was sent correctly
            assert len(self.state.chat) >= 1, self.state.chat

        # Tests at start:
        if iteration == 5:
            # No need to use try except as the travis test script checks for "Traceback" in STDOUT
            await self.test_botai_properties()
            await self.test_gamestate_static_variables()
            await self.test_game_info_static_variables()

        # Test actions:
        if "test_botai_actions1_successful" not in self.tests_done_by_name:
            if iteration >= 6:
                # Test actions
                await self.test_botai_actions1()
                # Test if actions were successful
                await self.test_botai_actions1_successful()

        elif "test_botai_actions2_successful" not in self.tests_done_by_name:
            if iteration >= 6:
                await self.test_botai_actions2()
                await self.test_botai_actions2_successful()

        elif "test_botai_actions3_successful" not in self.tests_done_by_name:
            if iteration >= 6:
                await self.test_botai_actions3()
                await self.test_botai_actions3_successful()

        elif "test_botai_actions4_successful" not in self.tests_done_by_name:
            if iteration >= 6:
                await self.test_botai_actions4()
                await self.test_botai_actions4_successful()

        elif "test_botai_actions5_successful" not in self.tests_done_by_name:
            if iteration >= 6:
                await self.test_botai_actions5()
                await self.test_botai_actions5_successful()



        # End when all tests successful
        if len(self.tests_done_by_name) >= self.tests_target:
            print("{}/{} Tests completed after {} seconds: {}".format(len(self.tests_done_by_name), self.tests_target, round(self.time, 1), self.tests_done_by_name))
            exit(0)

        # End time reached, cancel testing and report error: took too long
        if self.time >= self.game_time_timeout_limit:
            print("{}/{} Tests completed: {}".format(len(self.tests_done_by_name), self.tests_target, self.tests_done_by_name))
            print("Not all tests were successful. Timeout reached. Testing was aborted")
            exit(1000)



        """
        TODO BotAI tests:
        distribute workers, owned expansions, can cast, select build worker, can place, find placement, self build, chat send
        """



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
        assert self.can_afford(UnitTypeId.SCV)
        assert self.minerals >= 50, self.minerals
        assert self.vespene == 0, self.vespene
        assert self.supply_used == 12, self.supply_used
        assert self.supply_cap == 15, self.supply_cap
        assert self.supply_left == 3, self.supply_left
        self.tests_done_by_name.add("test_botai_properties")



    # Test BotAI action: train SCV
    async def test_botai_actions1(self):
        if self.can_afford(UnitTypeId.SCV):
            await self.do(self.townhalls.random.train(UnitTypeId.SCV))

    # Test BotAI action: move all SCVs to center of map
    async def test_botai_actions2(self):
        combined_actions = []
        center = self._game_info.map_center
        for scv in self.units(UnitTypeId.SCV):
            combined_actions.append(scv.move(center))
        await self.do_actions(combined_actions)

    # Test BotAI action: move some scvs to the center, some to minerals
    async def test_botai_actions3(self):
        combined_actions = []
        center = self._game_info.map_center
        scvs = self.workers
        scvs1 = scvs[:6]
        scvs2 = scvs[6:]
        for scv in scvs1:
            combined_actions.append(scv.move(center))
        mf = self.state.mineral_field.closest_to(self.townhalls.random)
        for scv in scvs2:
            combined_actions.append(scv.gather(mf))
        await self.do_actions(combined_actions)

    # Test BotAI action: move all SCVs to mine minerals near townhall
    async def test_botai_actions4(self):
        combined_actions = []
        mf = self.state.mineral_field.closest_to(self.townhalls.random)
        for scv in self.units(UnitTypeId.SCV):
            combined_actions.append(scv.gather(mf))
        await self.do_actions(combined_actions)

    # Test BotAI action: self.expand_now()
    async def test_botai_actions5(self):
        if self.can_afford(UnitTypeId.COMMANDCENTER) and not self.already_pending(UnitTypeId.COMMANDCENTER, all_units=True):
            await self.expand_now()


    # Test BotAI action results
    async def test_botai_actions1_successful(self):
        if self.already_pending(UnitTypeId.SCV, all_units=True) > 0:
            self.tests_done_by_name.add("test_botai_actions1_successful")

    async def test_botai_actions2_successful(self):
        if self.units.filter(lambda x: x.is_moving).amount >= 12:
            self.tests_done_by_name.add("test_botai_actions2_successful")

    async def test_botai_actions3_successful(self):
        if self.units.filter(lambda x: x.is_moving).amount >= 6:
            if self.units.gathering.amount >= 6:
                self.tests_done_by_name.add("test_botai_actions3_successful")

    async def test_botai_actions4_successful(self):
        if self.units.gathering.amount >= 12:
            self.tests_done_by_name.add("test_botai_actions4_successful")

    async def test_botai_actions5_successful(self):
        if self.units(UnitTypeId.COMMANDCENTER).amount >= 2:
            self.tests_done_by_name.add("test_botai_actions5_successful")



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
        self.tests_done_by_name.add("test_gamestate_static_variables")



    # Test self._game_info variables
    async def test_game_info_static_variables(self):
        assert len(self._game_info.players) == 2, self._game_info.players
        assert len(self._game_info.map_ramps) >= 2, self._game_info.map_ramps
        assert len(self._game_info.player_races) == 2, self._game_info.player_races
        # TODO: map size, pixel maps, playable area, player races, start locations, map center
        self.tests_done_by_name.add("test_game_info_static_variables")


    # TODO:
    # Test position.py
    # Test unit.py
    # Test units.py
    # Test ramp building placement position
    # Test client.py debug functions



def main():
    sc2.run_game(sc2.maps.get("(2)CatalystLE"), [
        Bot(Race.Terran, TestBot()),
        Computer(Race.Zerg, Difficulty.Easy)
    ], realtime=False)

if __name__ == '__main__':
    main()
