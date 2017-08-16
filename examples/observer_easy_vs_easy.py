import sys; sys.path.append(".")

from phyton import Race, Difficulty
from phyton import maps, run_game
from phyton.player import Computer

run_game(maps.get("Abyssal Reef LE"), [
    Computer(Race.Protoss, Difficulty.Easy),
    Computer(Race.Zerg, Difficulty.Easy)
])
