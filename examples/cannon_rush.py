import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

class CannonRushBot(sc2.BotAI):
    async def on_step(self, state, iteration):
        if iteration == 0:
            await self.chat_send("(probe)(pylon)(cannon)(cannon)(gg)")

        if not self.units(UnitTypeId.NEXUS).exists:
            for worker in self.workers:
                await self.do(worker.attack(self.enemy_start_locations[0]))
            return
        else:
            nexus = self.units(UnitTypeId.NEXUS).first

        if self.workers.amount < 16 and nexus.noqueue:
            if self.can_afford(UnitTypeId.PROBE):
                await self.do(nexus.train(UnitTypeId.PROBE))

        elif not self.units(UnitTypeId.PYLON).exists and not self.already_pending(UnitTypeId.PYLON):
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus)

        elif not self.units(UnitTypeId.FORGE).exists:
            pylon = self.units(UnitTypeId.PYLON).ready
            if pylon.exists:
                if self.can_afford(UnitTypeId.FORGE):
                    await self.build(UnitTypeId.FORGE, near=pylon.closest_to(nexus))

        elif self.units(UnitTypeId.PYLON).amount < 2:
            if self.can_afford(UnitTypeId.PYLON):
                pos = self.enemy_start_locations[0].towards(self.game_info.map_center, random.randrange(8, 15))
                await self.build(UnitTypeId.PYLON, near=pos)

        elif not self.units(UnitTypeId.PHOTONCANNON).exists:
            if self.units(UnitTypeId.PYLON).ready.amount >= 2 and self.can_afford(UnitTypeId.PHOTONCANNON):
                pylon = self.units(UnitTypeId.PYLON).closer_than(20, self.enemy_start_locations[0]).random
                await self.build(UnitTypeId.PHOTONCANNON, near=pylon)

        else:
            if self.can_afford(UnitTypeId.PYLON) and self.can_afford(UnitTypeId.PHOTONCANNON): # ensure "fair" decision
                for _ in range(20):
                    pos = self.enemy_start_locations[0].random_on_distance(random.randrange(5, 12))
                    building = UnitTypeId.PHOTONCANNON if state.psionic_matrix.covers(pos) else UnitTypeId.PYLON
                    r = await self.build(building, near=pos)
                    if not r: # success
                        break

def main():
    sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
        Bot(Race.Protoss, CannonRushBot()),
        Computer(Race.Protoss, Difficulty.Medium)
    ], realtime=False)

if __name__ == '__main__':
    main()
