import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.build_order import BuildOrder, supply_is, minerals_at_least, train, build, all_of
from sc2.player import Bot, Computer
from sc2.constants import *


def first_barracks(bot, state):
    return bot.units(UnitTypeId.BARRACKS).first


class TerranBuildOrderBot(sc2.BotAI):
    def __init__(self):
        build_order = [
            (supply_is(12), train(UnitTypeId.SCV, on_building=UnitTypeId.COMMANDCENTER)),
            (all_of(supply_is(13), minerals_at_least(100)), build(UnitTypeId.SUPPLYDEPOT)),
            (supply_is(13), train(UnitTypeId.SCV, on_building=UnitTypeId.COMMANDCENTER)),
            (supply_is(14), train(UnitTypeId.SCV, on_building=UnitTypeId.COMMANDCENTER)),
            (all_of(supply_is(15), minerals_at_least(150)), build(UnitTypeId.BARRACKS)),
            (supply_is(15), train(UnitTypeId.SCV, on_building=UnitTypeId.COMMANDCENTER)),
            (supply_is(16), train(UnitTypeId.SCV, on_building=UnitTypeId.COMMANDCENTER)),
            (supply_is(17), train(UnitTypeId.SCV, on_building=UnitTypeId.COMMANDCENTER)),
            (all_of(supply_is(18), minerals_at_least(150)), build(UnitTypeId.BARRACKS)),
            (supply_is(18), build(UnitTypeId.SUPPLYDEPOT, around_building=first_barracks)),
            (supply_is(18), train(UnitTypeId.SCV, on_building=UnitTypeId.COMMANDCENTER)),
        ]
        self.build_order = BuildOrder(self, build_order)

    async def on_step(self, state, iteration):
        await self.build_order.execute_build(state)
        cc = self.units(UnitTypeId.COMMANDCENTER).first
        for scv in self.units(UnitTypeId.SCV).idle:
            await self.do(scv.gather(self.state.mineral_field.closest_to(cc)))


run_game(maps.get("Abyssal Reef LE"), [
    Bot(Race.Terran, TerranBuildOrderBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=True)
