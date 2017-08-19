from sc2 import Race, Difficulty
from sc2 import maps, run_game
from sc2.player import Computer

run_game(maps.get("Abyssal Reef LE"), [
    Computer(Race.Protoss, Difficulty.Easy),
    Computer(Race.Zerg, Difficulty.Easy)
])
