import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

class ProxyRaxBot(sc2.BotAI):
    async def on_step(self, state, iteration):
        cc = self.units(UnitTypeId.COMMANDCENTER)
        if not cc.exists:
            target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
            for unit in self.workers | self.units(UnitTypeId.MARINE):
                await self.do(unit.attack(target))
            return
        else:
            cc = cc.first

        if self.units(UnitTypeId.MARINE).idle.amount > 15 and iteration % 50 == 1:
            target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
            for marine in self.units(UnitTypeId.MARINE).idle:
                await self.do(marine.attack(target))

        if self.can_afford(UnitTypeId.SCV) and self.workers.amount < 16 and cc.noqueue:
            await self.do(cc.train(UnitTypeId.SCV))

        elif self.supply_left < (2 if self.units(UnitTypeId.BARRACKS).amount < 3 else 4):
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 5))

        elif self.units(UnitTypeId.BARRACKS).amount < 3 or (self.minerals > 400 and self.units(UnitTypeId.BARRACKS).amount < 5):
            if self.can_afford(UnitTypeId.BARRACKS):
                p = self.game_info.map_center.towards(self.enemy_start_locations[0], 25)
                await self.build(UnitTypeId.BARRACKS, near=p)

        for rax in self.units(UnitTypeId.BARRACKS).ready.noqueue:
            if not self.can_afford(UnitTypeId.MARINE):
                break
            await self.do(rax.train(UnitTypeId.MARINE))

        for scv in self.units(UnitTypeId.SCV).idle:
            await self.do(scv.gather(self.state.mineral_field.closest_to(cc)))

def main():
    sc2.run_game(sc2.maps.get("Sequencer LE"), [
        Bot(Race.Terran, ProxyRaxBot()),
        Computer(Race.Zerg, Difficulty.Hard)
    ], realtime=False)

if __name__ == '__main__':
    main()
