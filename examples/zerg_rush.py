import random

import sc2
from sc2 import Race, Difficulty, ActionResult
from sc2.player import Bot, Computer

class ZergRushBot(sc2.BotAI):
    def __init__(self):
        self.drone_counter = 0
        self.overlord_counter = 0
        self.extractor_started = False
        self.spawning_pool_started = False
        self.moved_workers_to_gas = False
        self.moved_workers_from_gas = False
        self.queeen_started = False

    async def on_step(self, state, iteration):
        if not self.units("Hatchery").exists:
            for drone in self.units("Drone") | self.units("Zergling"):
                await self.do(drone("Attack", self.enemy_start_locations[0]))
            return

        hatchery = self.units("Hatchery").first
        larvae = self.units("Larva")

        for zl in self.units("Zergling").idle:
            await self.do(zl("Attack", self.enemy_start_locations[0]))

        for q in self.units("Queen").idle:
            await self.do(q("Effect Inject Larva", hatchery))

        if self.vespene >= 100:
            sp = self.units("Spawning Pool").ready
            if sp.exists and self.minerals >= 100:
                await self.do(sp.first("Research Zergling Metabolic Boost"))
                self.minerals -= 100

            if not self.moved_workers_from_gas:
                self.moved_workers_from_gas = True
                for drone in self.units("Drone"):
                    m = state.units("MineralField", name_exact=False).closer_than(drone.position, 10)
                    await self.do(drone("Gather", m.random, queue=True))

        if state.common.food_used > 20 and state.common.food_used + 2 > state.common.food_cap:
            if larvae.exists:
                if self.minerals >= self.units("Overlord").cost.minerals:
                    self.overlord_counter += 1
                    await self.do(larvae.random("Train Overlord"))
                return

        if self.units("Spawning Pool").ready.exists:
            if larvae.exists and self.minerals > self.units("Zergling").cost.minerals:
                for _ in range(min(larvae.amount, self.minerals // self.units("Zergling").cost.minerals)):
                    await self.do(larvae.random("Train Zergling"))
                    self.minerals -= self.units("Zergling").cost.minerals
                return

        if self.units("Extractor").ready.exists and not self.moved_workers_to_gas:
            self.moved_workers_to_gas = True
            extractor = self.units("Extractor").first
            for drone in self.units("Drone").random_group_of(3):
                await self.do(drone("Gather", extractor))

        if self.minerals > 500:
            for d in range(4, 15):
                pos = hatchery.position.to2.towards(self.game_info.map_center, d)
                if await self.can_place("Hatchery", pos):
                    self.spawning_pool_started = True
                    await self.do(self.units("Drone").random("Build Hatchery", pos))
                    break


        if larvae.exists:
            if self.drone_counter < 3:
                if self.minerals >= self.units("Drone").cost.minerals:
                    self.drone_counter += 1
                    await self.do(larvae.random("Train Drone"))
                    return

            elif self.overlord_counter == 0:
                if self.minerals >= self.units("Overlord").cost.minerals:
                    self.overlord_counter += 1
                    await self.do(larvae.random("Train Overlord"))
                    return

            elif self.drone_counter < 2:
                if self.minerals >= self.units("Drone").cost.minerals:
                    self.drone_counter += 1
                    await self.do(larvae.random("Train Drone"))
                    return

        if self.drone_counter > 1:
            if not self.extractor_started:
                if self.minerals >= self.units("Extractor").cost.minerals:
                    self.extractor_started = True
                    drone = self.units("Drone").random
                    target = state.units("VespeneGeyser").closest_to(drone.position)
                    await self.do(drone("Build Extractor", target))

            elif not self.spawning_pool_started:
                if self.minerals >= self.units("Spawning Pool").cost.minerals:

                    for d in range(4, 15):
                        pos = hatchery.position.to2.towards(self.game_info.map_center, d)
                        if await self.can_place("Spawning Pool", pos):
                            self.spawning_pool_started = True
                            drone = self.units("Drone").closest_to(pos)
                            await self.do(drone("Build Spawning Pool", pos))
                            break

            elif not self.queeen_started:
                if self.minerals >= self.units("Queen").cost.minerals:
                    r = await self.do(hatchery("Train Queen"))
                    if not r:
                        self.queeen_started = True


sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
    Bot(Race.Zerg, ZergRushBot()),
    Computer(Race.Protoss, Difficulty.Easy)
], realtime=True)
