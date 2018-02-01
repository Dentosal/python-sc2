# A StarCraft II API Client for Python 3

An easy-to-use library for writing AI Bots for StarCraft II in Python 3. The ultimate goal is simplicity and ease of use, while still preserving all functionality. A really simple worker rush bot should be no more than twenty lines of code, not two hundred. However, this library intends to provide both high and low level abstractions.

**This library (currently) covers only the raw scripted interface.** At this time I don't intend to add support for graphics-based interfaces.

Documentation is in [the Wiki](https://github.com/Dentosal/python-sc2/wiki).

## Installation

You'll need Python 3.6 or newer.

```
pip3 install --user --upgrade sc2
```

Please note that not all commits are not released to PyPI. Releases are tagged with version number. You can see latest released versions from [tags page](https://github.com/Dentosal/python-sc2/tags).

You'll also need an StarCraft II executable. If you are running Windows or macOS, just install the normal SC2 from blizzard app. [The free starter edition works too.](https://us.battle.net/account/sc2/starter-edition/). Linux users must use the [Linux binary](https://github.com/Blizzard/s2client-proto#downloads).

You probably want some maps too. Official map downloads are available from [Blizzard/s2client-proto](https://github.com/Blizzard/s2client-proto#downloads),

## Example

As promised, worker rush in less than twenty lines:

```python
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

class WorkerRushBot(sc2.BotAI):
    async def on_step(self, iteration):
        if iteration == 0:
            for worker in self.workers:
                await self.do(worker.attack(self.enemy_start_locations[0]))

run_game(maps.get("Abyssal Reef LE"), [
    Bot(Race.Zerg, WorkerRushBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=True)
```

This is probably the simplest bot that has any realistic chances of winning the game. I have ran it against the medium AI a few times, and once in a while it wins.

You can find more examples in the [`examples/`](/examples) folder.

## Bug reports, ideas and contributing

If you have any issues, ideas or feedback, please create [a new issue](https://github.com/Dentosal/python-sc2/issues/new). Pull requests are also welcome!
