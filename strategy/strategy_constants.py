from sc2.constants import *

from os.path import dirname
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


# NOTE: Adapt these paths in case of custom directories
dataset = "SC2ReplayStats/"
folder_sc2replays = dirname(dirname(ROOT_DIR)) + "/SC2-replays/" + dataset






eval_number_games = 1
max_iterations = 10000 # TODO set value # TODO test if cancels

min_units_attack = 15
min_units_defend = 5
distance_defend = 15

gameloops_check_frequency = 16

vespene_buildings = ("REFINERY", "ASSIMILATOR", "EXTRACTOR")
main_buildings = ("COMMANDCENTER", "NEXUS", "HATCHERY")
#workers = ("SCV", "DRONE", "PROBE")

# Note Hellbat is excluded, since its basically an ability of Hellion cf. https://liquipedia.net/starcraft2/Hellbat_(Legacy_of_the_Void)
# Additionally UnityTypeId.Hellbat does not exists
buildorder_excluded = ("SCV", "DRONE", "PROBE", "SUPPLYDEPOT", "PYLON", "OVERLORD", "HELLBAT") 

worker_expand_increase = 16
worker_gas_increase = 3

worker_supply = 1

init_supply = 12

# if more less auto_build_idle_limit idle buildings, build new ones
auto_build_idle_limit = 3

# 16 only mineral, will be increased automatically for gas
init_worker_count = 16

ending_folder = "/"
ending_csv = ".csv"
ending_sc2replay = ".SC2Replay"

race_terran_string = "Terr" # TODO fix R
race_protoss_string = "Prot" # TODO
race_zerg_string = "Zerg"

race_bot_separator = "vs"


folder_bot_replays = folder_sc2replays + "bot-replays/"
if not os.path.exists(folder_bot_replays):
    os.makedirs(folder_bot_replays)

folder_buildorder =  folder_sc2replays + "buildorders-csv/"
file_strategy = "strategy"+ending_csv

# http://liquipedia.net/starcraft2/Terran_Building_Statistics_(Legacy_of_the_Void)
# https://liquipedia.net/starcraft2/Terran_Units_(Legacy_of_the_Void)
construct_requirements = {
    UnitTypeId.BARRACKS : UnitTypeId.SUPPLYDEPOT,
    UnitTypeId.ORBITALCOMMAND : UnitTypeId.BARRACKS,
    UnitTypeId.FACTORY : UnitTypeId.BARRACKS,
    UnitTypeId.GHOSTACADEMY : UnitTypeId.BARRACKS,
    UnitTypeId.BUNKER : UnitTypeId.BARRACKS,
    UnitTypeId.STARPORT : UnitTypeId.FACTORY,
    UnitTypeId.ARMORY : UnitTypeId.FACTORY,
    UnitTypeId.FUSIONCORE : UnitTypeId.STARPORT,
    UnitTypeId.PLANETARYFORTRESS : UnitTypeId.ENGINEERINGBAY,
    UnitTypeId.SENSORTOWER : UnitTypeId.ENGINEERINGBAY,
    UnitTypeId.MISSILETURRET : UnitTypeId.ENGINEERINGBAY,
    UnitTypeId.STARPORTREACTOR :  UnitTypeId.STARPORT,
    UnitTypeId.STARPORTTECHLAB :  UnitTypeId.STARPORT,
    UnitTypeId.BARRACKSREACTOR:  UnitTypeId.BARRACKS,
    UnitTypeId.BARRACKSTECHLAB :  UnitTypeId.BARRACKS,
    UnitTypeId.FACTORYREACTOR:  UnitTypeId.FACTORY,
    UnitTypeId.FACTORYTECHLAB :  UnitTypeId.FACTORY,
    UnitTypeId.SUPPLYDEPOT : None,
    UnitTypeId.COMMANDCENTER : None,
    UnitTypeId.REFINERY : None
}


building_addons = {
    UnitTypeId.STARPORTREACTOR,
    UnitTypeId.STARPORTTECHLAB,
    UnitTypeId.BARRACKSREACTOR,
    UnitTypeId.BARRACKSTECHLAB,
    UnitTypeId.FACTORYREACTOR,
    UnitTypeId.FACTORYTECHLAB
}


# List: https://liquipedia.net/starcraft2/Terran_Units_(Legacy_of_the_Void)
unit_requirements = {
    UnitTypeId.MARINE : UnitTypeId.BARRACKS,
    UnitTypeId.MARAUDER : UnitTypeId.BARRACKSTECHLAB,
    UnitTypeId.REAPER : UnitTypeId.BARRACKS,
    UnitTypeId.GHOST : UnitTypeId.BARRACKSTECHLAB,
    UnitTypeId.HELLION : UnitTypeId.FACTORY,
    # TODO UnitTypeId.HELLBAT : UnitTypeId.FACTORY,
    UnitTypeId.SIEGETANK : UnitTypeId.FACTORYTECHLAB,
    UnitTypeId.CYCLONE : UnitTypeId.FACTORY,
    UnitTypeId.WIDOWMINE : UnitTypeId.FACTORY,
    UnitTypeId.THOR : UnitTypeId.FACTORYTECHLAB,
    UnitTypeId.VIKINGFIGHTER : UnitTypeId.STARPORT,
    UnitTypeId.MEDIVAC : UnitTypeId.STARPORT,
    UnitTypeId.LIBERATOR : UnitTypeId.STARPORT,
    UnitTypeId.RAVEN : UnitTypeId.STARPORTTECHLAB,
    UnitTypeId.BANSHEE : UnitTypeId.STARPORTTECHLAB,
    UnitTypeId.BATTLECRUISER : UnitTypeId.STARPORTTECHLAB
}


build_progress_completed = 1

# TODO reason why theses (fuzzy) limits
# for units
sufficently_enough_minerals = 800 # i.e. 2 times Battlecruiser or commandcenter
sufficently_enough_vespene = 600 # i.e. 2 times Battlecruiser

#for buildings
sufficently_much_minerals = sufficently_enough_minerals + 400 # i.e. 3 times commandcenter
sufficently_much_vespene = sufficently_enough_vespene + 150 # additional Planetary Fortress

terran_military_buildings = {
   UnitTypeId.STARPORT,
   UnitTypeId.FACTORY,
   UnitTypeId.BARRACKS
}

terran_military_buildings_sample = len(terran_military_buildings)

terran_military_units_mineral = {
    UnitTypeId.MARINE,
    UnitTypeId.HELLION
     #TODO UnitTypeId.HELLBAT
}

terran_military_units_mineral_sample = len(terran_military_units_mineral)

# note Viking == VIKINGFIGHTER
terran_military_units_vepene = {
    UnitTypeId.MARAUDER,
    UnitTypeId.REAPER,
    UnitTypeId.GHOST,
    UnitTypeId.SIEGETANK,
    UnitTypeId.CYCLONE,
    UnitTypeId.WIDOWMINE,
    UnitTypeId.THOR,
    UnitTypeId.MEDIVAC,
    UnitTypeId.LIBERATOR,
    UnitTypeId.RAVEN,
    UnitTypeId.BANSHEE,
    UnitTypeId.BATTLECRUISER,
    UnitTypeId.VIKINGFIGHTER
}

terran_military_units_vepene_sample = terran_military_buildings_sample + terran_military_units_mineral_sample

terran_military_units =  terran_military_units_mineral.union(terran_military_units_vepene)

