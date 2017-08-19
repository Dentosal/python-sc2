import random

import sc2
from sc2 import Race, Difficulty, ActionResult
from sc2.player import Bot, Computer

class CannonRushBot(sc2.BotAI):
    def __init__(self):
        self.proxy_pylon_pending = False

    def select_build_probe(self, state, pos, force=False):
        probes = self.units("Probe").closer_than(pos, 20)
        probes = probes if probes else self.units("Probe")
        for probe in probes.prefer_close_to(pos).prefer_idle:
            if not probe.orders:
                return probe
            if len(probe.orders) == 1 and probe.orders[0].ability.matches("Move"):
                return probe

        if force:
            return probes.random
        return None

    async def on_step(self, state, iteration):
        if not self.units("Nexus").exists:
            print("no nexus")
            return
        else:
            nexus = self.units("Nexus").first

        if self.units("Probe").amount < 13:
            if self.minerals >= self.units("Probe").cost.minerals:
                await self.do(nexus("Train Probe"))

        elif not self.units("Pylon").exists:
            if self.minerals >= self.units("Pylon").cost.minerals:
                for d in range(3, 20):
                    pos = nexus.position.to2.towards(self.game_info.map_center, d)
                    if await self.can_place("Pylon", pos):
                        probe = self.units("Probe").closest_to(pos)
                        error = await self.do(probe("Build Pylon", pos))

                        if error:
                            print(error)
                            exit("--")

                        await self.do(probe("Move", self.enemy_start_locations[0], queue=True))
                        break

        elif not self.units("Forge").exists:
            if self.units("Pylon").ready.exists:
                if self.minerals >= self.units("Forge").cost.minerals:
                    for d in range(3, 20):
                        pos = nexus.position.to2.towards(self.game_info.map_center, d)

                        if await self.can_place("Forge", pos):
                            assert state.psionic_matrix.covers(pos)
                            probe = self.units("Probe").closest_to(pos)
                            error = await self.do(probe("Build Forge", pos))

                            if error:
                                print(error)
                                exit("--")

                            await self.do(probe("Move", self.enemy_start_locations[0], queue=True))
                            break

        elif self.units("Pylon").amount < 2 and not self.proxy_pylon_pending:
            if self.minerals >= self.units("Pylon").cost.minerals:
                for d in range(12, 20):
                    pos = self.enemy_start_locations[0].towards(self.game_info.map_center, d)

                    if await self.can_place("Pylon", pos):
                        probe = self.units("Probe").closest_to(pos)
                        error = await self.do(probe("Build Pylon", pos))

                        if error and error != ActionResult.CantFindPlacementLocation:
                            print(error)
                            exit("--")

                        self.proxy_pylon_pending = True
                        break

        elif not self.units("Photon Cannon").exists:
            if self.units("Pylon").ready.amount >= 2:

                if self.minerals >= self.units("Photon Cannon").cost.minerals:
                    for _ in range(20):
                        pylon = self.units("Pylon").ready.closest_to(self.enemy_start_locations[0])

                        pos = pylon.position.towards_random_angle(
                            self.enemy_start_locations[0],
                            distance=random.randrange(1, 5)
                        )

                        if await self.can_place("Photon Cannon", pos):
                            assert state.psionic_matrix.covers(pos)

                            probe = self.select_build_probe(state, pos)
                            if not probe:
                                break

                            error = await self.do(probe("Build Photon Cannon", pos))

                            if error and error != ActionResult.CantFindPlacementLocation:
                                print(error)
                                exit("--")
                            break

        else:
            if self.minerals >= 150: # ensure "fair" decision
                for _ in range(20):
                    pos = self.enemy_start_locations[0].random_on_distance(random.randrange(5, 12))
                    building = "Photon Cannon" if state.psionic_matrix.covers(pos) else "Pylon"

                    if await self.can_place(building, pos):
                        probe = self.select_build_probe(state, pos)
                        if not probe:
                            break

                        error = await self.do(probe(f"Build {building}", pos))
                        break


sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
    Bot(Race.Protoss, CannonRushBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=True)
