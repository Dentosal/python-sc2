import sc2
from sc2 import run_game, maps, Race, Difficulty
from time import gmtime, strftime
from sc2.constants import *
from sc2.player import Bot, Computer

from zerg_bot_buildorder import Zerg_Bot_Buildorder
from protoss_bot_buildorder import Protoss_Bot_Buildorder
from terran_bot_buildorder import Terran_Bot_Buildorder

def main():
    map_name = "Catalyst LE"
    self_race = Race.Terran
    enemy_race = Race.Terran

    race_to_string = {
        Race.Terran:  race_terran_string,
        Race.Zerg: race_zerg_string,
        Race.Protoss: race_protoss_string
    }


    self_race_string =  race_to_string[self_race]
    enemy_race_string = race_to_string[enemy_race]
    time = strftime("%Y-%m-%d-%H:%M:%S", gmtime())
    output_replay = map_name + self_race_string + race_bot_separator + enemy_race_string

    bot_selector = {
        Race.Terran:  Terran_Bot_Buildorder,
        Race.Zerg: Zerg_Bot_Buildorder,
        Race.Protoss: Protoss_Bot_Buildorder
    }

    hash = "1cc609b79314bee713eb2e3708c3ae4d2a03762c"#"90145ee27487043a70b38e4346100dd882197036"
        
    folder = folder_buildorder + self_race_string + race_bot_separator + enemy_race_string + ending_folder + map_name + ending_folder
    path = folder + hash + ending_csv


    run_game(maps.get(map_name), [
        Bot(self_race, bot_selector[self_race](path)),
        Computer(enemy_race, Difficulty.Easy)
    ], realtime=False, save_replay_as= output_replay)

if __name__ == '__main__':
    main()
