import sc2
from sc2 import Race, Difficulty
from sc2.build_orders.build_order import train_unit, BuildOrder, morph
from sc2.build_orders.commands import add_gas, construct, expand, add_supply
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.state_conditions.conditions import supply_at_least, all_of, unit_count, gas_less_than, unit_count_less_than, \
    unit_count_at_least


def research(building, upgrade):
    async def research_spec(bot,state):
        sp = bot.units(building).ready
        if sp.exists and bot.can_afford(upgrade) and not bot.already_pending(upgrade):
            await bot.do(sp.first(upgrade))

    return research_spec

class ZergRushBot(sc2.BotAI):

    def __init__(self):
        self.attack = False
        self.mboost_started = False
        build_order = [
            (all_of(supply_at_least(13), unit_count(UnitTypeId.OVERLORD, 1, include_pending=True)), add_supply(prioritize=True)),
            (all_of(supply_at_least(17), unit_count(UnitTypeId.EXTRACTOR, 0, include_pending=True)), add_gas()),
            (all_of(supply_at_least(17), unit_count(UnitTypeId.SPAWNINGPOOL, 0, include_pending=True)), construct(UnitTypeId.SPAWNINGPOOL)),
            (all_of(supply_at_least(17), unit_count(UnitTypeId.HATCHERY, 1, include_pending=True)), expand()),
            (supply_at_least(18), morph(UnitTypeId.ZERGLING)),
            (supply_at_least(19), train_unit(UnitTypeId.QUEEN, on_building=UnitTypeId.HATCHERY, prioritize=True)),
            (all_of(supply_at_least(21), unit_count(UnitTypeId.OVERLORD, 2, include_pending=True)), add_supply(prioritize=True)),
            (all_of(supply_at_least(21), unit_count(UnitTypeId.ROACHWARREN, 0, include_pending=True)), construct(UnitTypeId.ROACHWARREN)),
            (all_of(supply_at_least(20), unit_count(UnitTypeId.OVERLORD, 3, include_pending=True)), add_supply(prioritize=True)),
            (unit_count_at_least(UnitTypeId.ROACH, 7), morph(UnitTypeId.ZERGLING, repeatable=True)),
            (unit_count(UnitTypeId.ROACHWARREN, 1), morph(UnitTypeId.ROACH, repeatable=True))
        ]

        self.build_order = BuildOrder(self, build_order, worker_count=35)

    async def on_step(self, state, iteration):
        await self.distribute_workers()

        if self.vespene >= 100:
            sp = self.units(UnitTypeId.SPAWNINGPOOL).ready
            if sp.exists and self.minerals >= 100 and not self.mboost_started:
                await self.do(sp.first(AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST))
                self.mboost_started = True

        await self.build_order.execute_build(state)

        for queen in self.units(UnitTypeId.QUEEN).idle:
            if queen.energy >= 25:  # Hard coded, since this is not (yet) available
                hatchery = self.townhalls.closest_to(queen.position.to2)
                await self.do(queen(AbilityId.INJECTLARVA, hatchery))

        if (self.units(UnitTypeId.ROACH).amount >= 7 and self.units(UnitTypeId.ZERGLING).amount >= 10) or self.attack:
            self.attack = True
            for unit in self.units(UnitTypeId.ZERGLING).ready.idle | self.units(UnitTypeId.ROACH).ready.idle:
                await self.do(unit.attack(self.enemy_start_locations[0]))
                if self.known_enemy_structures.exists:
                    enemy = self.known_enemy_structures.first
                    await self.do(unit.attack(enemy.position.to2, queue=True))
            return

def main():
    sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
        Bot(Race.Zerg, ZergRushBot()),
        Computer(Race.Random, Difficulty.Hard)
    ], realtime=False)

if __name__ == '__main__':
    main()
