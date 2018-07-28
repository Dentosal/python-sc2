import sc2
from sc2 import run_game, maps, Race, Difficulty
from time import gmtime, strftime
from strategy_constants import *
from sc2.player import Bot, Computer
import time
import pandas as pd
from random import uniform
import sys
from bot_ai_extended import Bot_AI_Extended
import logging
from util import create_folder

def get_buildorder_hash(path_strategy, method):
    """Determines the build-order"""

    if method == no_hash:
        return method

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
                
    folder = folder_buildorder + self_race_string + race_bot_separator + enemy_race_string + ending_folder + map_name + ending_folder
    path_strategy = folder + file_strategy 

     # Logging based on: https://docs.python.org/3/howto/logging-cookbook.html
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      
    logger_strategy = logging.getLogger("sc2.strategy")     

    loggers = [logging.getLogger("sc2.bot_ai"), logging.getLogger("sc2.controller"), logging.getLogger("sc2.main"),
               logging.getLogger("sc2.maps"), logging.getLogger("sc2.paths"), logging.getLogger("sc2.sc2process"),
               logging.getLogger("sc2.protocol"), logging.getLogger("root"), logging.getLogger("sc2.command"), logger_strategy,
               logging.getLogger("sc2.performance")]
    


      
    for i in range(eval_number_games):    

        print("Evaluation number: {0}".format(i+1))
        
        hash = get_buildorder_hash(path_strategy, method) 
        
        path = folder + hash + ending_csv
        time_string = str(round(time.time())) 
        id = map_name + self_race_string + race_bot_separator + enemy_race_string + time_string + "_" + hash

        subpath = method +  ending_folder + map_name + ending_folder

        create_folder(folder_bot_replays + subpath)
        create_folder(folder_bot_logs + subpath)

        output_replay = folder_bot_replays + subpath +  id + ending_sc2replay
        log_file_path = folder_bot_logs + subpath + id + ending_logs
                       
        fh = logging.FileHandler(log_file_path, mode = "w") 
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG) 
        
        # add output to path to loggers
        for logger in loggers:
            logger.addHandler(fh)
        
        logger_strategy.info("Log file: {0}".format(log_file_path))
        logger_strategy.info("Selected build-order hash: {0}".format(hash))
        logger_strategy.info("Outputfile will be {0}".format(output_replay))
        logger_strategy.info("ID: {0}".format(id))

        # Start game
        run_game(maps.get(map_name), [
            Bot(self_race, Bot_AI_Extended(path, output_replay, logger_strategy)),
            #Bot(self_race, Bot_AI_Extended(path, output_replay, logger_strategy))
            Computer(enemy_race, enemy_difficulty)
        ], realtime=False, save_replay_as= output_replay, game_time_limit = max_gametime)


        for logger in loggers:
            logger.removeHandler(fh)

        fh.flush()
        fh.close()

        logging.shutdown()   
    
if __name__ == '__main__':
    main()
