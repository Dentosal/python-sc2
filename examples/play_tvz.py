import sc2
from sc2 import Race
from sc2.player import Human, Bot

from zerg_rush import ZergRushBot
from baneling_bust import BanelingBustBot
from cannon_rush import CannonRushBot

def main():
    sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
        Human(Race.Protoss),
        # Bot(Race.Protoss, CannonRushBot())
        # Bot(Race.Zerg, ZergRushBot())
        Bot(Race.Zerg, BanelingBustBot())
    ], realtime=False)

if __name__ == '__main__':
    main()
