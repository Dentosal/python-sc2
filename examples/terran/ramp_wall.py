import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.position import Point2, Point3


class RampWallBot(sc2.BotAI):
    async def on_step(self, iteration):
        cc = self.units(COMMANDCENTER)
        if not cc.exists:
            return
        else:
            cc = cc.first

        if self.can_afford(SCV) and self.workers.amount < 16 and cc.noqueue:
            await self.do(cc.train(SCV))


        # Raise depos when enemies are nearby
        for depo in self.units(SUPPLYDEPOT).ready:
            for unit in self.known_enemy_units.not_structure:
                if unit.position.to2.distance_to(depo.position.to2) < 15:
                    break
            else:
                await self.do(depo(MORPH_SUPPLYDEPOT_LOWER))

        # Lower depos when no enemies are nearby
        for depo in self.units(SUPPLYDEPOTLOWERED).ready:
            for unit in self.known_enemy_units.not_structure:
                if unit.position.to2.distance_to(depo.position.to2) < 10:
                    await self.do(depo(MORPH_SUPPLYDEPOT_RAISE))
                    break

        depot_placement_positions = self.main_base_ramp.corner_depots
        # Uncomment the following if you want to build 3 supplydepots in the wall instead of a barracks in the middle + 2 depots in the corner
        # depot_placement_positions = self.main_base_ramp.corner_depots | {self.main_base_ramp.depot_in_middle}

        barracks_placement_position = None
        barracks_placement_position = self.main_base_ramp.barracks_correct_placement
        # If you prefer to have the barracks in the middle without room for addons, use the following instead
        # barracks_placement_position = self.main_base_ramp.barracks_in_middle

        depots = self.units(SUPPLYDEPOT) | self.units(SUPPLYDEPOTLOWERED)

        # Filter locations close to finished supply depots
        if depots:
            depot_placement_positions = {d for d in depot_placement_positions if depots.closest_distance_to(d) > 1}

        # Build depots
        if self.can_afford(SUPPLYDEPOT) and not self.already_pending(SUPPLYDEPOT):
            if len(depot_placement_positions) == 0:
                return
            # Choose any depot location
            target_depot_location = depot_placement_positions.pop()
            ws = self.workers.gathering
            if ws: # if workers were found
                w = ws.random
                await self.do(w.build(SUPPLYDEPOT, target_depot_location))

        # Build barracks
        if depots.ready.exists and self.can_afford(BARRACKS) and not self.already_pending(BARRACKS):
            if self.units(BARRACKS).amount + self.already_pending(BARRACKS) > 0:
                return
            ws = self.workers.gathering
            if ws and barracks_placement_position: # if workers were found
                w = ws.random
                await self.do(w.build(BARRACKS, barracks_placement_position))



def main():
    sc2.run_game(sc2.maps.get("OdysseyLE"), [
        Bot(Race.Terran, RampWallBot()),
        Computer(Race.Zerg, Difficulty.Hard)
    ], realtime=False)

if __name__ == '__main__':
    main()
