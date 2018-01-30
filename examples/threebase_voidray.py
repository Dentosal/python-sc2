import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

class ThreebaseVoidrayBot(sc2.BotAI):
    def select_target(self, state):
        if self.known_enemy_structures.exists:
            return random.choice(self.known_enemy_structures)

        return self.enemy_start_locations[0]

    async def on_step(self, state, iteration):
        if iteration == 0:
            await self.chat_send("(glhf)")

        if not self.units(UnitTypeId.NEXUS).ready.exists:
            for worker in self.workers:
                await self.do(worker.attack(self.enemy_start_locations[0]))
            return
        else:
            nexus = self.units(UnitTypeId.NEXUS).ready.random

        for idle_worker in self.workers.idle:
            mf = state.mineral_field.closest_to(idle_worker)
            await self.do(idle_worker.gather(mf))

        if self.units(UnitTypeId.VOIDRAY).amount > 10 and iteration % 50 == 0:
            for vr in self.units(UnitTypeId.VOIDRAY).idle:
                await self.do(vr.attack(self.select_target(state)))

        for a in self.units(UnitTypeId.ASSIMILATOR):
            if a.assigned_harvesters < a.ideal_harvesters:
                w = self.workers.closer_than(20, a)
                if w.exists:
                    await self.do(w.random.gather(a))

        if self.supply_left < 2 and not self.already_pending(UnitTypeId.PYLON):
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus)
            return

        if self.workers.amount < self.units(UnitTypeId.NEXUS).amount*15 and nexus.noqueue:
            if self.can_afford(UnitTypeId.PROBE):
                await self.do(nexus.train(UnitTypeId.PROBE))

        elif not self.units(UnitTypeId.PYLON).exists and not self.already_pending(UnitTypeId.PYLON):
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus)

        if self.units(UnitTypeId.NEXUS).amount < 3 and not self.already_pending(UnitTypeId.NEXUS):
            if self.can_afford(UnitTypeId.NEXUS):
                location = await self.get_next_expansion()
                await self.build(UnitTypeId.NEXUS, near=location)

        if self.units(UnitTypeId.PYLON).ready.exists:
            pylon = self.units(UnitTypeId.PYLON).ready.random
            if self.units(UnitTypeId.GATEWAY).ready.exists:
                if not self.units(UnitTypeId.CYBERNETICSCORE).exists:
                    if self.can_afford(UnitTypeId.CYBERNETICSCORE) and not self.already_pending(UnitTypeId.CYBERNETICSCORE):
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
            else:
                if self.can_afford(UnitTypeId.GATEWAY) and not self.already_pending(UnitTypeId.GATEWAY):
                    await self.build(UnitTypeId.GATEWAY, near=pylon)

        for nexus in self.units(UnitTypeId.NEXUS).ready:
            vgs = state.vespene_geyser.closer_than(20.0, nexus)
            for vg in vgs:
                if not self.can_afford(UnitTypeId.ASSIMILATOR):
                    break

                worker = self.select_build_worker(vg.position)
                if worker is None:
                    break

                if not self.units(UnitTypeId.ASSIMILATOR).closer_than(1.0, vg).exists:
                    await self.do(worker.build(UnitTypeId.ASSIMILATOR, vg))

        if self.units(UnitTypeId.PYLON).ready.exists and self.units(UnitTypeId.CYBERNETICSCORE).ready.exists:
            pylon = self.units(UnitTypeId.PYLON).ready.random
            if self.units(UnitTypeId.STARGATE).amount < 3 and not self.already_pending(UnitTypeId.STARGATE):
                if self.can_afford(UnitTypeId.STARGATE):
                    await self.build(UnitTypeId.STARGATE, near=pylon)

        for sg in self.units(UnitTypeId.STARGATE).ready.noqueue:
            if self.can_afford(UnitTypeId.VOIDRAY):
                await self.do(sg.train(UnitTypeId.VOIDRAY))

def main():
    sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
        Bot(Race.Protoss, ThreebaseVoidrayBot()),
        Computer(Race.Protoss, Difficulty.Easy)
    ], realtime=False)

if __name__ == '__main__':
    main()
