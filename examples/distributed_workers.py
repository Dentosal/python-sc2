import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import logging

logger = logging.getLogger(__name__)

class TerranBot(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_supply()
        await self.build_geyser()
        await self.build_workers()
        await self.expand()

    async def build_workers(self):
        for cc in self.units(UnitTypeId.COMMANDCENTER).ready.noqueue:
            if self.can_afford(UnitTypeId.SCV):
                await self.do(cc.train(UnitTypeId.SCV))

    async def expand(self):
        if self.units(UnitTypeId.COMMANDCENTER).amount < 3 and self.can_afford(UnitTypeId.COMMANDCENTER):
            await self.expand_now()

    async def build_supply(self):
        ccs = self.units(UnitTypeId.COMMANDCENTER).ready
        if ccs.exists:
            cc = ccs.first
            if self.supply_left < 4 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
                if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                    await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 5))

    async def build_geyser(self):
        for CC in self.units(UnitTypeId.COMMANDCENTER):
            # get the number of nearby refineries
            nearby_refineries = []
            for refinery in self.units(UnitTypeId.REFINERY):
                logging.warn(CC.distance_to(refinery))
                if CC.distance_to(refinery) < 10:
                    nearby_refineries.append(refinery)
            refineries_to_build = 2 - len(nearby_refineries)
            if refineries_to_build <= 0:
                return

            # get a worker from the CC
            scv = self.workers.closest_to(CC)

            # get the closest geyser
            target = self.state.vespene_geyser.closest_to(scv.position)
            if scv.position.distance_to(target) < 25 and self.can_afford(UnitTypeId.REFINERY) and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
                err = await self.do(scv.build(UnitTypeId.REFINERY, target))



run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, TerranBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=False)
