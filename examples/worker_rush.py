import sys; sys.path.append(".")
import phyton
from phyton import Race, Difficulty
from phyton import maps, run_game
from phyton.player import Bot, Computer

class WorkerRushBot(phyton.BotAI):
    def __init__(self):
        pass

run_game(maps.get("Abyssal Reef LE"), [
    Bot(Race.Protoss, WorkerRushBot()),
    Computer(Race.Protoss, Difficulty.Medium)
])
