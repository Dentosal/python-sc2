import csv
import pandas as pd
from sc2.build_orders.build_order import *
from sc2.state_conditions.conditions import  supply_at_least, cum_supply_at_least, all_of, unit_count_at_least, unit_count_at_least_completed
from sc2.build_orders.commands import construct, expand, add_supply, add_gas, research
from strategy_constants import *
from sc2.data import *
import sc2
from sc2 import Race
import re
from random import uniform, randrange
import os
from math import isclose
from util import print_log, measure_runtime
import logging

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

def export_result(bot, result): 
    """Appends result to a specified file"""
    if bot.path is None:
        return

    df = pd.DataFrame(data = {"File": [os.path.basename(bot.path)], "Map": [bot.map], "Method": [bot.method], "Result": [result]})

    if os.path.isfile(file_bot_results):
        df.to_csv(file_bot_results, mode = "a", header = False, index=False)          
    else:
        df.to_csv(file_bot_results, header = ["File", "Map", "Method", "Result"], index=False)     


def init_build_order(path, logger):
    """Parse csv file to build order"""

    build_order = []

    if no_hash in path:
        return build_order

    
    df = pd.read_csv(path, sep=";")

    for index, row in df.iterrows():
        supply = row['TotalSupply']
        type = row['Type']
        unit_building = row['OnBuilding']
        unit_supply = row['Supply']
   
        unit_name = row['UnitName']

        # exlude automatic builded units
        if unit_name in buildorder_excluded:
            continue

        # check if its addon to a building
        if type == "Building":
            try:
                building_sep = re.findall('[A-Z][^A-Z]*', unit_name)
                if(len(building_sep)>= 2):
                    building_str = building_sep[0].upper()
                    building = UnitTypeId[building_str]
                    # if it not fails --> addon e.g. BarracksReactor
                    type = "Unit" # addon can be trained as unit
                    unit_building = building_str
            except (NameError, KeyError):
                pass
 
        unit_name = unit_name.upper()       

        if(type == "Building"):
            if(unit_name in vespene_buildings): # race_gas
                build_order.append((cum_supply_at_least(supply), add_gas()))
            elif(unit_name in main_buildings): # race_basic_townhalls
                build_order.append((cum_supply_at_least(supply), expand(repeatable=False)))
            else:
                build_order.append((cum_supply_at_least(supply), construct(UnitTypeId[unit_name])))
        elif(type == "Unit"):
            unit_building = unit_building.upper()
            build_order.append((all_of(cum_supply_at_least(supply), unit_count_at_least(UnitTypeId[unit_building], 1, include_pending=False)), train_unit(UnitTypeId[unit_name], on_building = UnitTypeId[unit_building], increased_supply = unit_supply)))
        elif(type == "Upgrade"):           
            unit_building = unit_building.upper()
            upgrade = ""
            building = ""
            prefix_buildings = ["BARRACKS", "STARPORT", "FACTORY", ""]
            # Adapt to Ids
            unit_name = unit_name.replace("ARMORSLEVEL", "ARMORLEVEL")
            unit_name = unit_name.replace("TERRANVEHICLEANDSHIPARMOR", "TERRANVEHICLEANDSHIPPLATING") 

           
            unit_name = unit_name.replace("DRILLCLAWS", "DRILLINGCLAWS")
            unit_name = unit_name.replace("TERRANBUILDINGARMOR", "TERRANSTRUCTUREARMORUPGRADE")
     

            if not unit_building == "TECHLAB":
                prefix_buildings = [""]
           
            for option_building in prefix_buildings:
                
                if option_building+unit_building+"RESEARCH_"+unit_name in AbilityId.__members__:
                    upgrade = option_building+unit_building+"RESEARCH_"+unit_name
                    building = option_building + unit_building
                    break
                elif option_building+"RESEARCH_"+unit_name in AbilityId.__members__:
                    upgrade = option_building+"RESEARCH_"+unit_name
                    building = option_building + unit_building
                    break
            
            if upgrade == "":
                print_log(logger, logging.ERROR, "Upgrade {0} not found".format(unit_name))
                continue
            else:
                print_log(logger, logging.DEBUG, "Upgrade {0} on building {1} found".format(upgrade, building))


            build_order.append((all_of(supply_at_least(supply), unit_count_at_least_completed(UnitTypeId[building], 1)), 
                                    research(AbilityId[upgrade], on_building = UnitTypeId[building])))

            
    return build_order
        
