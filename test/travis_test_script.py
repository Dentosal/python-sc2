import sys
import importlib

import sc2
from sc2.player import Bot, Computer
from sc2.data import Race, Difficulty

def convert_input_string(string: str):
    # example input: examples/protoss/cannon_rush.py
    return string.rstrip("py").rstrip(".").replace("/", ".")

def find_bot_class(bot_module):
    module_vars = vars(bot_module)
    for key in module_vars.keys():
        if "Bot" in key and "Bot" != key:
            print(key)
            return module_vars[key]
    return None

def find_bot_race(bot_path):
    if "protoss" in bot_path.lower():
        return Race.Protoss
    if "terran" in bot_path.lower():
        return Race.Terran
    if "zerg" in bot_path.lower():
        return Race.Zerg

def run_bot(bot_class, race):
    game_result = sc2.run_game(sc2.maps.get("(2)CatalystLE"), [
        Bot(race, bot_class()),
        Computer(Race.Terran, Difficulty.Medium)
    ], realtime=False)
    return game_result

if len(sys.argv) > 1:
    bot_path = sys.argv[1]
    bot_import_path = convert_input_string(bot_path)
    bot_module = importlib.import_module(bot_import_path)
    bot = find_bot_class(bot_module)
    bot_race = find_bot_race(bot_path)

    print("Running bot: {}".format(bot))
    result = run_bot(bot, bot_race)

    # 1 means the bot won, 2 means the bot lost, anything else means the game crashed
    print(result)
    if result is not None and result.value in [1, 2]:
        exit(0)
    exit(1)
exit(2)