import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

class ZergRushBot(sc2.BotAI):
    def __init__(self):
        self.drone_counter = 0
        self.extractor_started = False
        self.spawning_pool_started = False
        self.moved_workers_to_gas = False
        self.moved_workers_from_gas = False
        self.queeen_started = False
        self.mboost_started = False

    async def on_step(self, state, iteration):
        if iteration == 0:
            await self.chat_send("(glhf)")

        if not self.units(UnitTypeId.HATCHERY).ready.exists:
            for unit in self.workers | self.units(UnitTypeId.ZERGLING) | self.units(UnitTypeId.QUEEN):
                await self.do(unit.attack(self.enemy_start_locations[0]))
            return

        hatchery = self.units(UnitTypeId.HATCHERY).ready.first
        larvae = self.units(UnitTypeId.LARVA)

        target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
        for zl in self.units(UnitTypeId.ZERGLING).idle:
            await self.do(zl.attack(target))

        for UnitTypeId.QUEEN in self.units(UnitTypeId.QUEEN).idle:
            if UnitTypeId.QUEEN.energy >= 25: # Hard coded, since this is not (yet) available
                await self.do(UnitTypeId.QUEEN(AbilityId.INJECTLARVA, hatchery))

        if self.vespene >= 100:
            sp = self.units(UnitTypeId.SPAWNINGPOOL).ready
            if sp.exists and self.minerals >= 100 and not self.mboost_started:
                await self.do(sp.first(AbilityId.ZERGLINGMOVEMENTSPEED))
                self.mboost_started = True

            if not self.moved_workers_from_gas:
                self.moved_workers_from_gas = True
                for drone in self.workers:
                    m = state.mineral_field.closer_than(10, drone.position)
                    await self.do(drone.gather(m.random, queue=True))

        if self.supply_left < 2:
            if self.can_afford(UnitTypeId.OVERLORD) and larvae.exists:
                await self.do(larvae.random.train(UnitTypeId.OVERLORD))

        if self.units(UnitTypeId.SPAWNINGPOOL).ready.exists:
            if larvae.exists and self.can_afford(UnitTypeId.ZERGLING):
                await self.do(larvae.random.train(UnitTypeId.ZERGLING))

        if self.units(UnitTypeId.EXTRACTOR).ready.exists and not self.moved_workers_to_gas:
            self.moved_workers_to_gas = True
            extractor = self.units(UnitTypeId.EXTRACTOR).first
            for drone in self.workers.random_group_of(3):
                await self.do(drone.gather(extractor))

        if self.minerals > 500:
            for d in range(4, 15):
                pos = hatchery.position.to2.towards(self.game_info.map_center, d)
                if await self.can_place(UnitTypeId.HATCHERY, pos):
                    self.spawning_pool_started = True
                    await self.do(self.workers.random.build(UnitTypeId.HATCHERY, pos))
                    break

        if self.drone_counter < 3:
            if self.can_afford(UnitTypeId.DRONE):
                self.drone_counter += 1
                await self.do(larvae.random.train(UnitTypeId.DRONE))

        if not self.extractor_started:
            if self.can_afford(UnitTypeId.EXTRACTOR):
                drone = self.workers.random
                target = state.vespene_geyser.closest_to(drone.position)
                err = await self.do(drone.build(UnitTypeId.EXTRACTOR, target))
                if not err:
                    self.extractor_started = True

        elif not self.spawning_pool_started:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                for d in range(4, 15):
                    pos = hatchery.position.to2.towards(self.game_info.map_center, d)
                    if await self.can_place(UnitTypeId.SPAWNINGPOOL, pos):
                        drone = self.workers.closest_to(pos)
                        err = await self.do(drone.build(UnitTypeId.SPAWNINGPOOL, pos))
                        if not err:
                            self.spawning_pool_started = True
                            break

        elif not self.queeen_started and self.units(UnitTypeId.SPAWNINGPOOL).ready.exists:
            if self.can_afford(UnitTypeId.QUEEN):
                r = await self.do(hatchery.train(UnitTypeId.QUEEN))
                if not r:
                    self.queeen_started = True

def main():
    sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
        Bot(Race.Zerg, ZergRushBot()),
        Computer(Race.Terran, Difficulty.Medium)
    ], realtime=True)

if __name__ == '__main__':
    main()
