from .ids.ability_id import *
from .ids.buff_id import *
from .ids.effect_id import *
from .ids.unit_typeid import *
from .ids.upgrade_id import *

import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

vespene_buildings = ("REFINERY", "ASSIMILATOR", "EXTRACTOR")
main_buildings = ("COMMANDCENTER", "NEXUS", "HATCHERY")
#workers = ("SCV", "DRONE", "PROBE")

worker_expand_increase = 16
worker_gas_increase = 3

worker_supply = 1

init_supply = 12

# 16 only mineral, 21 for mineral and vespene, 22 leads to worker gathering minerals far away
init_worker_count = 16

ending_folder = "/"
ending_csv = ".csv"
ending_sc2replay = ".SC2Replay"

race_terran_string = "Terr"
race_protoss_string = "Prot"
race_zerg_string = "Zerg"

race_bot_separator = "vs"

folder_buildorder = os.path.dirname(ROOT_DIR) + "/buildorders/"


# http://liquipedia.net/starcraft2/Terran_Building_Statistics_(Legacy_of_the_Void)
construct_requirements = {
    UnitTypeId.STARPORT : UnitTypeId.FACTORY
}