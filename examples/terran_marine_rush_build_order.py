import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.build_orders.build_order import BuildOrder, train_unit
from sc2.build_orders.commands import construct, expand, add_supply
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.state_conditions.conditions import all_of, supply_at_least, minerals_at_least, unit_count


def first_barracks(bot):
    return bot.units(UnitTypeId.BARRACKS).first


class TerranBuildOrderBot(sc2.BotAI):
    def __init__(self):
        build_order = [
            (supply_at_least(13), add_supply(prioritize=True)),
            (supply_at_least(15), construct(UnitTypeId.BARRACKS, prioritize=True)),
            (supply_at_least(16), construct(UnitTypeId.BARRACKS, prioritize=True)),
            (supply_at_least(16), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(17), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(18), construct(UnitTypeId.BARRACKS, prioritize=True)),
            (supply_at_least(18), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(19), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(20), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(21), add_supply(prioritize=True)),
            (supply_at_least(21), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(22), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(23), construct(UnitTypeId.BARRACKS, prioritize=True)),
            (supply_at_least(23), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(24), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(25), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(26), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(27), construct(UnitTypeId.BARRACKS, prioritize=True)),
            (all_of(supply_at_least(27), unit_count(UnitTypeId.BARRACKS, 5, include_pending=True)), add_supply(prioritize=True)),
            (unit_count(UnitTypeId.BARRACKS, 5), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS, repeatable=True))
        ]
        self.attack = False
        self.build_order = BuildOrder(self, build_order, worker_count=16)

    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_order.execute_build()

        if self.units(UnitTypeId.MARINE).amount >= 15 or self.attack:
            self.attack = True
            for unit in self.units(UnitTypeId.MARINE).idle:
                await self.do(unit.attack(self.enemy_start_locations[0]))
                if self.known_enemy_structures.exists:
                    enemy = self.known_enemy_structures.first
                    await self.do(unit.attack(enemy.position.to2, queue=True))
            return


def main():
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, TerranBuildOrderBot()),
        # Bot(Race.Terran, TerranBuildOrderBot()),
        Computer(Race.Random, Difficulty.Harder)
    ], realtime=False)

if __name__ == '__main__':
    main()

