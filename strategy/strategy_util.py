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

def can_build(building, unit):
    # TODO check if unit requires addon
    if unit_requirements[unit] in building_addons and building.has_add_on:
        return isclose(building.build_progress, build_progress_completed) and building.is_mine and building.noqueue and building.is_idle
    else:
        return isclose(building.build_progress, build_progress_completed) and building.is_mine and building.noqueue and building.is_idle

    

def export_result(self, result): 

    if self.path is None:
        return

    df = pd.DataFrame(data = {"file": [os.path.basename(self.path)], "result": [result]})

    if os.path.isfile(file_bot_results):
        df.to_csv(file_bot_results, mode = "a", header = False)          
    else:
        df.to_csv(file_bot_results, header = ["path","result"])     


def init_build_order(path, logger):

    build_order = []
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
            unit_name = unit_name.replace("ARMORSLEVEL", "ARMORLEVEL")
            
            unit_name = unit_name.replace("TERRANVEHICLEANDSHIPARMOR", "TERRANVEHICLEANDSHIPPLATING") 


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
                print_log(logger, logging.WARNING, "Upgrade {0} not found".format(unit_name))
                continue
            else:
                print_log(logger, logging.DEBUG, "Upgrade {0} on building {1} found".format(upgrade, building))


            build_order.append((all_of(supply_at_least(supply), unit_count_at_least_completed(UnitTypeId[building], 1)), 
                                    research(AbilityId[upgrade], on_building = UnitTypeId[building])))

            
    return build_order
        