import sys; sys.path.append(".")
import sc2
from sc2 import Race, Difficulty, command
from sc2.player import Bot, Computer

class WorkerRushBot(sc2.BotAI):
    def on_start(self, enemy_start_locations):
        self.enemy_start_locations = enemy_start_locations

    def on_step(self, state, iteration):
        if iteration > 0:
            return
        for unit in state.units:
            if unit.is_visible and unit.is_mine and not unit.is_structure:
                yield unit("Attack", self.enemy_start_locations[0])

sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
    Bot(Race.Protoss, WorkerRushBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=True)
