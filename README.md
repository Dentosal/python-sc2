# A StarCraft II API Client for Python 3

An easy-to-use library for writing StarCraft II AI Bots in Python 3. The ultimate goal is simplicity and ease of use, while still preserving all functionality. A simple worker rush bot takes no more than twenty lines of code, not two hundred. However, this library intends to provide both high and low level abstractions.

**This library (currently) covers only the raw scripted interface.** At this time I don't intend to add support for graphics-based interfaces.

Documentation is in [the Wiki](https://github.com/Dentosal/python-sc2/wiki).

For automatically running multiple matches, check out [Dentosal/sc2-bot-match-runner](https://github.com/Dentosal/sc2-bot-match-runner).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installation

You'll need Python 3.6 or newer. Install the library via pip:

```
pip3 install --user --upgrade sc2
```

Please note that not all commits are not released to PyPI. Releases are tagged with version number. You can see the latest released versions in the [tags page](https://github.com/Dentosal/python-sc2/tags).

You'll also need a StarCraft II executable. If you are running Windows or macOS, just install SC2 from the Blizzard app. The [free starter edition](https://us.battle.net/account/sc2/starter-edition/) works too. Linux users must use the [Linux binary](https://github.com/Blizzard/s2client-proto#downloads).

Finally, you'll need to download some maps. Official map downloads are available from [Blizzard/s2client-proto](https://github.com/Blizzard/s2client-proto#downloads). Follow the instructions in the link to download map files into subdirectories of your `<sc2-install-dir>/Maps` directory.

### Running

After installing the library, a StarCraft II executable, and some maps, you're ready to get started. Simply run a bot file to fire up an instance of StarCraft II with the bot running. For example:

```
python3 examples/cannon_rush.py
```

## Example

As promised, [worker rush](examples/worker_rush.py) in less than twenty lines:

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

This is probably the simplest bot that has any realistic chance of winning the game. I have run it against the medium AI a few times, and once in a while it wins.

You can find more examples in the [`examples/`](/examples) folder.

## Contributing

If you have any issues, ideas or feedback, please [create a new issue](https://github.com/Dentosal/python-sc2/issues/new). Pull requests are also welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
