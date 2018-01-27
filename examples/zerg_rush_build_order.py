import random

import sc2
from sc2 import Race, Difficulty
from sc2.build_orders.build_order import train, expand, build, BuildOrder, morph, Intent
from sc2.build_orders.state_conditions import supply_at_least, all_of, minerals_at_least, unit_count
from sc2.constants import *
from sc2.player import Bot, Computer

def add_gas():
    async def add_gas_spec(bot, state):
        for th in bot.townhalls:
            for nexus in bot.units(th.type_id).ready:
                vgs = state.vespene_geyser.closer_than(20.0, nexus)
                for vg in vgs:
                    if not bot.can_afford(UnitTypeId.EXTRACTOR):
                        break

                    worker = bot.select_build_worker(vg.position)
                    if worker is None:
                        break

                    if not bot.units(UnitTypeId.EXTRACTOR).closer_than(1.0, vg).exists:
                        return await bot.do(worker.build(UnitTypeId.EXTRACTOR, vg))
        return sc2.ActionResult.Error
    return Intent(add_gas_spec)

def research(building, upgrade):
    async def research_spec(bot,state):
        sp = bot.units(building).ready
        if sp.exists and bot.can_afford(upgrade) and not bot.already_pending(upgrade):
            await bot.do(sp.first(upgrade))

    return research_spec

class ZergRushBot(sc2.BotAI):

    def __init__(self):
        self.attack = False
        build_order = [
            (all_of(supply_at_least(13), unit_count(UnitTypeId.OVERLORD, 1, include_pending=True)), morph(UnitTypeId.OVERLORD)),
            (all_of(supply_at_least(17), unit_count(UnitTypeId.EXTRACTOR, 0, include_pending=True)), add_gas()),
            (all_of(supply_at_least(17), unit_count(UnitTypeId.SPAWNINGPOOL, 0, include_pending=True)), build(UnitTypeId.SPAWNINGPOOL)),
            (all_of(supply_at_least(17), unit_count(UnitTypeId.HATCHERY, 1, include_pending=True)), expand()),
            (supply_at_least(18), morph(UnitTypeId.ZERGLING)),
            (supply_at_least(19), train(UnitTypeId.QUEEN, on_building=UnitTypeId.HATCHERY)),
            (all_of(supply_at_least(21), unit_count(UnitTypeId.OVERLORD, 2, include_pending=True)), morph(UnitTypeId.OVERLORD)),
            (all_of(supply_at_least(21), unit_count(UnitTypeId.ROACHWARREN, 0, include_pending=True)), build(UnitTypeId.ROACHWARREN)),
            (all_of(supply_at_least(20), unit_count(UnitTypeId.OVERLORD, 3, include_pending=True)), morph(UnitTypeId.OVERLORD)),
            (unit_count(UnitTypeId.ROACH, 0, include_pending=True), morph(UnitTypeId.ROACH)),
            (unit_count(UnitTypeId.ROACH, 1, include_pending=True), morph(UnitTypeId.ROACH)),
            (unit_count(UnitTypeId.ROACH, 2, include_pending=True), morph(UnitTypeId.ROACH)),
            (unit_count(UnitTypeId.ROACH, 3, include_pending=True), morph(UnitTypeId.ROACH)),
            (unit_count(UnitTypeId.ROACH, 4, include_pending=True), morph(UnitTypeId.ROACH)),
            (unit_count(UnitTypeId.ROACH, 5, include_pending=True), morph(UnitTypeId.ROACH)),
            (unit_count(UnitTypeId.ROACH, 6, include_pending=True), morph(UnitTypeId.ROACH)),
            (None, morph(UnitTypeId.ZERGLING).keep_going())
        ]

        self.build_order = BuildOrder(self, build_order, worker_count=35)

    async def on_step(self, state, iteration):
        # await self.distribute_workers()
        await self.build_order.execute_build(state)
        if self.units(UnitTypeId.ROACH).amount >= 7 or self.attack:
            self.attack = True
            for unit in self.units(UnitTypeId.ZERGLING) | self.units(UnitTypeId.ROACH):
                await self.do(unit.attack(self.enemy_start_locations[0]))
            return

def main():
    sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
        Bot(Race.Zerg, ZergRushBot()),
        Computer(Race.Terran, Difficulty.Medium)
    ], realtime=True)

if __name__ == '__main__':
    main()
