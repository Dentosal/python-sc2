import sc2
from sc2 import run_game, maps, Race, Difficulty
from time import gmtime, strftime
from strategy_constants import *
from sc2.player import Bot, Computer
from zerg_bot_buildorder import Zerg_Bot_Buildorder
from protoss_bot_buildorder import Protoss_Bot_Buildorder
from terran_bot_buildorder import Terran_Bot_Buildorder
import time


import pandas as pd
from random import uniform, randrange

def get_buildorder_hash(path_strategy, method):
    """Determines the build-order"""
    df = pd.read_csv(path_strategy, sep=";", decimal=b',')

    r = uniform(0,1)
    
    # All build-orders of strategy [method] have a weight of ]0,1]
    # searches for the first occurances, where the weight is larger than r to determine hash/build-order
    for index, row in df.iterrows():
        weight = row[method]
        if weight >= r: 
            return row["Hash"]


def main():
    """Determine build-order and start game"""
    self_race_string =  race_to_string[self_race]
    enemy_race_string = race_to_string[enemy_race]
    
    bot_selector = {
        Race.Terran: Terran_Bot_Buildorder,
        Race.Zerg: Zerg_Bot_Buildorder,
        Race.Protoss: Protoss_Bot_Buildorder
    }


            
    folder = folder_buildorder + self_race_string + race_bot_separator + enemy_race_string + ending_folder + map_name + ending_folder
    path_strategy = folder + file_strategy 
      
    for i in range(eval_number_games):    
        
        hash = get_buildorder_hash(path_strategy, method)
        print("Selected buildorder: {0}".format(hash))

        path = folder + hash + ending_csv

        time_string = str(round(time.time())) #strftime("%Y-%m-%d-%H:%M:%S", gmtime())
        output_replay = folder_bot_replays + map_name + self_race_string + race_bot_separator + enemy_race_string + time_string + "_" + hash + ending_sc2replay

        print("Outputfile will be {0}".format(output_replay))

        # Start game
        run_game(maps.get(map_name), [
            Bot(self_race, bot_selector[self_race](path)),
            Computer(enemy_race, enemy_difficulty)
        ], realtime=False, save_replay_as= output_replay, game_time_limit = max_gametime)

if __name__ == '__main__':
    main()
