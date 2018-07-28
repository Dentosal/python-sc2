from sc2 import Race, Difficulty
from sc2.constants import *
from bot_config import *
import os
from util import create_folder
# NOTE: constants are partially tailored to Terran specific units due to underlying data set

# Setup -----------------------------------------------------------------------

# Dataset name
dataset = "DataSetSc2ReplayStats"
# NOTE: Adapt these paths in case of custom directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
folder_sc2replays = os.path.dirname(os.path.dirname(ROOT_DIR)) + "/SC2-replays/" + dataset + "/"


# Eval settings ---------------------------------------------------------------

# Number of games to play
eval_number_games = 30

# CatalystLE
map_name = "Catalyst LE" # "Blackpink LE", "Catalyst LE" # TODO list all 7 maps
method = "NoBuildOrder" # "BestEqualWeighted"
self_race = Race.Terran
enemy_race = Race.Terran
enemy_difficulty = Difficulty.Hard



# Files -----------------------------------------------------------------------

# File endings
ending_folder = "/"
ending_csv = ".csv"
ending_sc2replay = ".SC2Replay"
ending_logs = ".log"

# Strings for file names
race_terran_string = "Terran"
race_protoss_string = "Protoss"
race_zerg_string = "Zerg"
race_bot_separator = "vs"

folder_bot_replays = folder_sc2replays + "bot-replays/"
folder_bot_logs = folder_sc2replays + "bot-logs/"

create_folder(folder_bot_replays)
create_folder(folder_bot_logs)

no_hash = "NoBuildOrder"


folder_buildorder =  folder_sc2replays + "buildorders-csv/"
file_strategy = "strategy"+ending_csv

file_bot_results = folder_bot_replays + "results.csv"

# Strategy util constants -----------------------------------------------------

vespene_buildings = ("REFINERY", "ASSIMILATOR", "EXTRACTOR")
main_buildings = ("COMMANDCENTER", "NEXUS", "HATCHERY")

# Note Hellbat is excluded, since its basically an ability of Hellion 
# cf. https://liquipedia.net/starcraft2/Hellbat_(Legacy_of_the_Void)
# Additionally UnityTypeId.Hellbat does not exists
buildorder_excluded = ("SCV", "DRONE", "PROBE", "SUPPLYDEPOT", "PYLON", "OVERLORD", "HELLBAT") 

result_won = "won"
result_lost = "lost"


race_to_string = {
        Race.Terran:  race_terran_string,
        Race.Zerg: race_zerg_string,
        Race.Protoss: race_protoss_string
    }

# Terran buildings and units --------------------------------------------------

# Sources:
# http://liquipedia.net/starcraft2/Terran_Building_Statistics_(Legacy_of_the_Void)
# https://liquipedia.net/starcraft2/Terran_Units_(Legacy_of_the_Void)


# Requirements for buildings
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


# Terran reseach requirements
research_requirements = {
    AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYARMORLEVEL2 : UnitTypeId.ARMORY,
    AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYARMORLEVEL3 : UnitTypeId.ARMORY,
    AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL2: UnitTypeId.ARMORY,
    AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL3 : UnitTypeId.ARMORY,
    AbilityId.RESEARCH_ADVANCEDBALLISTICS : UnitTypeId.FUSIONCORE,
    AbilityId.RESEARCH_DRILLINGCLAWS : UnitTypeId.ARMORY,
    AbilityId.FACTORYTECHLABRESEARCH_RESEARCHTRANSFORMATIONSERVOS : UnitTypeId.ARMORY
}



# Terran units requirements
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

# Terran units requirements
unit_requirements_2nd = {
    UnitTypeId.MARINE : None,
    UnitTypeId.MARAUDER : None,
    UnitTypeId.REAPER : None,
    UnitTypeId.GHOST : None,
    UnitTypeId.HELLION : None,
    UnitTypeId.SIEGETANK : None,
    UnitTypeId.CYCLONE : None,
    UnitTypeId.WIDOWMINE : None,
    UnitTypeId.THOR : UnitTypeId.ARMORY,
    UnitTypeId.VIKINGFIGHTER : None,
    UnitTypeId.MEDIVAC : None,
    UnitTypeId.LIBERATOR : None,
    UnitTypeId.RAVEN : None,
    UnitTypeId.BANSHEE : None,
    UnitTypeId.BATTLECRUISER : UnitTypeId.FUSIONCORE
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



auto_build_factory_units = [UnitTypeId.HELLION, UnitTypeId.CYCLONE]
#auto_build_factory_units_length = len(auto_build_factory_units)

auto_build_barracks_units = [UnitTypeId.MARINE, UnitTypeId.REAPER]

auto_build_starport_units = [UnitTypeId.VIKINGFIGHTER, UnitTypeId.MEDIVAC, UnitTypeId.LIBERATOR]