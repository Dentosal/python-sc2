# Phyton - A StarCraft II bot api client library for Python 3

Phyton is an easy-to-use library for wrting AI Bots for StarCraft II in Python 3. The ultimate goal is simplicity and ease of use, while still preserving all funcionality. A really simple worker rush bot should be no more than twenty lines of code, not two hundred. This library covers only the scripted (raw) interface.

As promised, a simple worker rush in less than twenty lines of code:

```python
import phyton
from phyton import run_game, maps, Race, Difficulty, command
from phyton.player import Bot, Computer

class WorkerRushBot(phyton.BotAI):
    def on_start(self, enemy_start_locations):
        self.enemy_start_locations = enemy_start_locations

    def on_step(self, state, iteration):
        if iteration > 0:
            return
        for unit in state.units:
            if unit.is_visible and unit.is_mine and not unit.is_structure:
                yield command("Attack", self.enemy_start_locations[0], unit)

run_game(maps.get("Abyssal Reef LE"), [
    Bot(Race.Protoss, WorkerRushBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=True)
```
