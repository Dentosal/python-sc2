import random

from PIL import Image

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.position import Point2

class RampWallBot(sc2.BotAI):
    @property
    def next_ramp_top(self):
        cc = self.units(COMMANDCENTER).first

        ramps = sorted(self.game_info.map_ramps, key=lambda r: cc.distance_to(r.top_center))

        for ramp in ramps:
            if (self.units(SUPPLYDEPOT) | self.units(SUPPLYDEPOTLOWERED)).closer_than(8, ramp.top_center).amount < 3:
                break
        else:
            return None

        self.game_info.placement_grid

        exit("??")

    async def on_step(self, iteration):
        cc = self.units(COMMANDCENTER)
        if not cc.exists:
            return
        else:
            cc = cc.first

        if self.can_afford(SCV) and self.workers.amount < 16 and cc.noqueue:
            await self.do(cc.train(SCV))

        if self.can_afford(SUPPLYDEPOT):
            await self.build(SUPPLYDEPOT, near=self.next_ramp_top, placement_step=1, random_alternative=False)

        for depo in self.units(SUPPLYDEPOT).ready:
            await self.do(depo(MORPH_SUPPLYDEPOT_LOWER))

        for scv in self.units(SCV).idle:
            await self.do(scv.gather(self.state.mineral_field.closest_to(cc)))

def main():
    sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, RampWallBot()),
        Computer(Race.Zerg, Difficulty.Hard)
    ], realtime=False)

if __name__ == '__main__':
    main()
