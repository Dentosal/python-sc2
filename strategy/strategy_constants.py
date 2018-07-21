from sc2.constants import *
from os.path import dirname
import os
# NOTE: constants are partially tailored to Terran specific units due to underlying data set

# Setup -----------------------------------------------------------------------

# Dataset name
dataset = "DataSetSc2ReplayStats"
# NOTE: Adapt these paths in case of custom directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
folder_sc2replays = dirname(dirname(ROOT_DIR)) + "/SC2-replays/" + dataset + "/"



# Files -----------------------------------------------------------------------

# File endings
ending_folder = "/"
ending_csv = ".csv"
ending_sc2replay = ".SC2Replay"

# Strings for file names
race_terran_string = "Terran"
race_protoss_string = "Protoss"
race_zerg_string = "Zerg"
race_bot_separator = "vs"


folder_bot_replays = folder_sc2replays + "bot-replays/"
if not os.path.exists(folder_bot_replays):
    os.makedirs(folder_bot_replays)

folder_buildorder =  folder_sc2replays + "buildorders-csv/"
file_strategy = "strategy"+ending_csv


# Strategy util constants -----------------------------------------------------

vespene_buildings = ("REFINERY", "ASSIMILATOR", "EXTRACTOR")
main_buildings = ("COMMANDCENTER", "NEXUS", "HATCHERY")

# Note Hellbat is excluded, since its basically an ability of Hellion 
# cf. https://liquipedia.net/starcraft2/Hellbat_(Legacy_of_the_Void)
# Additionally UnityTypeId.Hellbat does not exists
buildorder_excluded = ("SCV", "DRONE", "PROBE", "SUPPLYDEPOT", "PYLON", "OVERLORD", "HELLBAT") 


# Minimum number of resources to perform an upgrade
# Maximum costs for Terran upgrades are 300 i.e. ShipPlatingLevel3
min_resource_upgrades = 300 

# Minimum number of resources to autobuild units
sufficently_enough_minerals = 800 # i.e. 2 times Battlecruiser or commandcenter
sufficently_enough_vespene = 600 # i.e. 2 times Battlecruiser

# Minimum number of resources to autobuild buildings
sufficently_much_minerals = sufficently_enough_minerals + 400 # i.e. 3 times commandcenter
sufficently_much_vespene = sufficently_enough_vespene + 150 # additional Planetary Fortress


# Game settings ---------------------------------------------------------------

# Number of games to play
eval_number_games = 1
# Maximum time in seconds until game result is Tie
max_gametime = 900 # TODO set value in seconds

# Minimum amount of units to attack
min_units_attack = 15
# Minimum amount of units to defend
min_units_defend = 5
# Maximum military units when giving up
max_units_giveup = min_units_defend
# Maximum distance to defend against enemy units
distance_defend = 15

# 16 iterations == 1 second
gameloops_check_frequency = 16

# Amount of new workers per expansion
worker_expand_increase = 16

# Amount of new workers per new gas resource
worker_gas_increase = 3

# Supply of a single worker
worker_supply = 1

# Initial supply
init_supply = 12

# if more less auto_build_idle_limit idle buildings, build new ones
auto_build_idle_limit = 3

# 16 only mineral, will be increased automatically for gas
init_worker_count = 16

# Check for isclose if build is completed
build_progress_completed = 1


result_won = "won"
result_lost = "lost"

# Terran buildings and units --------------------------------------------------


# Requirements for buildings
# Sources:
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
    UnitTypeId.REFINERY : None,
    UnitTypeId.ENGINEERINGBAY : None,
    UnitTypeId.ARMORY:  UnitTypeId.FACTORY
}

# Available Building Addons
building_addons = {
    UnitTypeId.STARPORTREACTOR,
    UnitTypeId.STARPORTTECHLAB,
    UnitTypeId.BARRACKSREACTOR,
    UnitTypeId.BARRACKSTECHLAB,
    UnitTypeId.FACTORYREACTOR,
    UnitTypeId.FACTORYTECHLAB
}


# Terran units requirements: https://liquipedia.net/starcraft2/Terran_Units_(Legacy_of_the_Void)
unit_requirements = {
    UnitTypeId.MARINE : UnitTypeId.BARRACKS,
    UnitTypeId.MARAUDER : UnitTypeId.BARRACKSTECHLAB,
    UnitTypeId.REAPER : UnitTypeId.BARRACKS,
    UnitTypeId.GHOST : UnitTypeId.BARRACKSTECHLAB,
    UnitTypeId.HELLION : UnitTypeId.FACTORY,
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


# Terran military buildings
terran_military_buildings = {
   UnitTypeId.STARPORT,
   UnitTypeId.FACTORY,
   UnitTypeId.BARRACKS
}



# Terran military units requiring just minerals and no vespene
terran_military_units_mineral = {
    UnitTypeId.MARINE,
    UnitTypeId.HELLION
}



# Terran military units requiring minerals and vespene  
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
    UnitTypeId.VIKINGFIGHTER # Viking == VIKINGFIGHTER
}

# All Terran military units
terran_military_units =  terran_military_units_mineral.union(terran_military_units_vepene)

# Length 
terran_military_units_mineral_sample = len(terran_military_units_mineral)
terran_military_buildings_sample = len(terran_military_buildings)
terran_military_units_vepene_sample = terran_military_buildings_sample + terran_military_units_mineral_sample



