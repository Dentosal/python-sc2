import sc2
from sc2 import run_game, maps, Race, Difficulty
from time import gmtime, strftime
from strategy_constants import *
from sc2.player import Bot, Computer, Human
import time
import pandas as pd
from random import uniform
import sys
from bot_ai_extended import Bot_AI_Extended
import logging
from util import create_folder
from strategy_util import get_buildorder_hash

def main():

    self_race_string =  race_to_string[self_race]
    enemy_race_string = race_to_string[enemy_race]

    folder = folder_buildorder + self_race_string + race_bot_separator + enemy_race_string + ending_folder + map_name_strategy + ending_folder
    path_strategy = folder + file_strategy 

    hash = get_buildorder_hash(path_strategy, method) 

    path = folder + hash + ending_csv
       
    sc2.run_game(sc2.maps.get(map_name), [
        Human(Race.Terran),
        Bot(Race.Terran, Bot_AI_Extended(path, method = "Human", map = map_name))
    ], realtime=True)

if __name__ == '__main__':
    main()

