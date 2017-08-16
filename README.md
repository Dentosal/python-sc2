# A StarCraft II bot api client library for Python 3

An easy-to-use library for wrting AI Bots for StarCraft II in Python 3. The ultimate goal is simplicity and ease of use, while still preserving all funcionality. A really simple worker rush bot should be no more than twenty lines of code, not two hundred.

**This library (currently) covers only the raw scripted interface.** At this time I don't ident to add support for graphics-based iterfaces.

## Installation

```
pip3 install --upgrade git+https://github.com/Dentosal/python-sc2
```

You'll also need an StarCraft II executable. If you are running Windows or macOS, just install the normal SC2 from blizzard app. [The free starter edition works too.](https://us.battle.net/account/sc2/starter-edition/). Linux users must use the [Linux binary](https://github.com/Blizzard/s2client-proto#downloads).

You probably want some maps too. Offical map downloads are available from [Blizzard/s2client-proto](https://github.com/Blizzard/s2client-proto#downloads),

## Example

As promised, worker rush in less than twenty lines:

```python
import sc2
from sc2 import run_game, maps, Race, Difficulty, command
from sc2.player import Bot, Computer

class WorkerRushBot(sc2.BotAI):
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

This is probably the simplest bot that has any realistic chances of winning the game. I have ran it against the medium AI quite a few times, and once in a while it wins.
