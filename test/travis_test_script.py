import sys, subprocess
# import importlib
#
# import sc2
# from sc2.player import Bot, Computer
# from sc2.data import Race, Difficulty

# def convert_input_string(string: str):
#     # example input: examples/protoss/cannon_rush.py
#     return string.rstrip("py").rstrip(".").replace("/", ".")
#
# def find_bot_class(bot_module):
#     module_vars = vars(bot_module)
#     for key in module_vars.keys():
#         if "Bot" in key and "Bot" != key:
#             print(key)
#             return module_vars[key]
#     return None
#
# def find_bot_race(bot_path):
#     if "examples/protoss" in bot_path.lower():
#         return Race.Protoss
#     if "examples/terran" in bot_path.lower():
#         return Race.Terran
#     if "examples/zerg" in bot_path.lower():
#         return Race.Zerg
#     if "examples/burnys" in bot_path.lower():
#         return Race.Terran
#
# def run_bot(bot_class, race):
#     game_result = sc2.run_game(sc2.maps.get("(2)CatalystLE"), [
#         Bot(race, bot_class()),
#         Computer(Race.Terran, Difficulty.Medium)
#     ], realtime=False)
#     return game_result

if len(sys.argv) > 1:
    result = subprocess.run(["python", sys.argv[1]], stdout=subprocess.PIPE)
    print_output: str = result.stdout.decode('utf-8')
    print(print_output)
    linebreaks = [
        ["\r\n", print_output.count("\r\n")],
        ["\r", print_output.count("\r")],
        ["\n", print_output.count("\n")],
    ]
    most_linebreaks_type = max(linebreaks, key=lambda x: x[1])
    linebreak_type, linebreak_count = most_linebreaks_type
    output_as_list = print_output.split(linebreak_type)

    # bot_path = sys.argv[1]
    # bot_import_path = convert_input_string(bot_path)
    # bot_module = importlib.import_module(bot_import_path)
    # bot = find_bot_class(bot_module)
    # bot_race = find_bot_race(bot_path)

    # print("Running bot: {} from file {}".format(bot, __file__))
    # result = run_bot(bot, bot_race)

    # 1 means the bot won, 2 means the bot lost, anything else means the game crashed
    if result.returncode in [1, 2]:
        for line in output_as_list:
            # This will throw an error if a bot is called Traceback
            if "Traceback" in line:
                print("Exiting with exit code 3, error:\r\n{}".format(output_as_list))
                exit(3)
        print("Exiting with exit code 0")
        exit(0)
    # Exit code 1: bot crashed
    print("Exiting with exit code 1")
    exit(1)
# Exit code 2: bot was not launched
print("Exiting with exit code 2")
exit(2)