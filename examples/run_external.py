import sys
import asyncio

import sc2
from sc2 import Race
from sc2.player import Bot

from zerg_rush import ZergRushBot

def main(pc):
    if pc:
        host = False
        portconfig = sc2.portconfig.Portconfig.from_json(pc)
    else:
        host = True
        portconfig = sc2.portconfig.Portconfig()
        print(portconfig.as_json)

    player_config = [
        Bot(Race.Zerg, None),
        Bot(Race.Zerg, None)
    ]

    player_config[0 if host else 1].ai = ZergRushBot()

    if host:
        g = sc2.main._host_game(
            sc2.maps.get("Abyssal Reef LE"),
            player_config,
            realtime=True,
            portconfig=portconfig
        )
    else:
        g = sc2.main._join_game(
            player_config,
            realtime=True,
            portconfig=portconfig
        )

    result = asyncio.get_event_loop().run_until_complete(g)
    print(result)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
