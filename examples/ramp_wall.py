import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

class RampWallBot(sc2.BotAI):
    async def on_step(self, iteration):
        cc = self.units(COMMANDCENTER)
        if not cc.exists:
            return
        else:
            cc = cc.first

        if self.can_afford(SCV) and self.workers.amount < 16 and cc.noqueue:
            await self.do(cc.train(SCV))

        # elif self.supply_left < (2 if self.units(BARRACKS).amount < 3 else 4):
        # if self.can_afford(SUPPLYDEPOT):
        #     await self.build(SUPPLYDEPOT, near=cc.position.towards_with_random_angle(self.game_info.map_center, distance=15))

        self.game_info.placement_grid.save_image("placement_grid.png")
        self.game_info.pathing_grid.save_image("pathing_grid.png")
        self.game_info.map_ramps.save_image("ramps.png")

        ramps = self.game_info.map_ramps
        data = [(self.game_info.pathing_grid[x, y],0,ramps[x, y]) for y in range(ramps.height) for x in range(ramps.width)]
        from PIL import Image
        im= Image.new('RGB', (ramps.width, ramps.height))
        im.putdata(data)
        im.save("combined.png")
        exit()

def main():
    sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, RampWallBot()),
        Computer(Race.Zerg, Difficulty.Hard)
    ], realtime=False)

if __name__ == '__main__':
    main()
