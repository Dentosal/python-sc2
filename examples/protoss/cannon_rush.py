import os
import random
import platform
from pathlib import Path

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

class CannonRushBot(sc2.BotAI):
    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("(probe)(pylon)(cannon)(cannon)(gg)")

        if not self.units(NEXUS).exists:
            for worker in self.workers:
                await self.do(worker.attack(self.enemy_start_locations[0]))
            return
        else:
            nexus = self.units(NEXUS).first

        if self.workers.amount < 16 and nexus.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

        elif not self.units(PYLON).exists and not self.already_pending(PYLON):
            if self.can_afford(PYLON):
                await self.build(PYLON, near=nexus)

        elif not self.units(FORGE).exists:
            pylon = self.units(PYLON).ready
            if pylon.exists:
                if self.can_afford(FORGE):
                    await self.build(FORGE, near=pylon.closest_to(nexus))

        elif self.units(PYLON).amount < 2:
            if self.can_afford(PYLON):
                pos = self.enemy_start_locations[0].towards(self.game_info.map_center, random.randrange(8, 15))
                await self.build(PYLON, near=pos)

        elif not self.units(PHOTONCANNON).exists:
            if self.units(PYLON).ready.amount >= 2 and self.can_afford(PHOTONCANNON):
                pylon = self.units(PYLON).closer_than(20, self.enemy_start_locations[0]).random
                await self.build(PHOTONCANNON, near=pylon)

        else:
            if self.can_afford(PYLON) and self.can_afford(PHOTONCANNON): # ensure "fair" decision
                for _ in range(20):
                    pos = self.enemy_start_locations[0].random_on_distance(random.randrange(5, 12))
                    building = PHOTONCANNON if self.state.psionic_matrix.covers(pos) else PYLON
                    r = await self.build(building, near=pos)
                    if not r: # success
                        break

def main():
    basedir = {
        "Windows": "C:/Program Files (x86)/StarCraft II",
        "Darwin": "/Applications/StarCraft II",
        "Linux": "~/StarCraftII"
    }
    binpath = {
        "Windows": "SC2_x64.exe",
        "Darwin": "SC2.app/Contents/MacOS/SC2",
        "Linux": "SC2_x64"
    }
    pf = platform.system()
    base = Path(os.environ.get("SC2PATH", basedir[pf])).expanduser()
    if (base / "maps").exists():
        maps = base / "maps"
    else:
        maps = base / "Maps"
    if not maps.exists():
        maps.mkdir()

    try:
        sc2.maps.get("(2)CatalystLE")
    except KeyError:
        ladder2017_season4_url = 'http://blzdistsc2-a.akamaihd.net/MapPacks/Ladder2017Season4.zip'
        maps_password = "iagreetotheeula"

        os.system(
            f'wget -O /tmp/z.$$ {ladder2017_season4_url} && '
            f'unzip -P {maps_password} -j /tmp/z.$$ "Ladder2017Season4/CatalystLE.SC2Map" -d "{str(maps)}"'
            f'&& mv "{str(maps)}/CatalystLE.SC2Map" "{str(maps)}/(2)CatalystLE.SC2Map"'
        )

    sc2.run_game(sc2.maps.get("(2)CatalystLE"), [
        Bot(Race.Protoss, CannonRushBot()),
        Computer(Race.Protoss, Difficulty.Medium)
    ], realtime=False)

if __name__ == '__main__':
    main()
