import csv
import pandas as pd
from sc2.build_orders.build_order import train_unit
from sc2.state_conditions.conditions import  supply_at_least, cum_supply_at_least
from sc2.build_orders.commands import construct, expand, add_supply, add_gas
from sc2.constants import *
from sc2.data import *
import sc2
from sc2 import Race
import re

def race_to_string(race):
    if race == Race.Terran:
        return(race_terran_string)
    elif race == Race.Protoss:
        return(race_protoss_string)
    elif race == Race.Zerg:
        return(race_zerg_string)


def init_build_order(path):

    build_order = []
    df = pd.read_csv(path, sep=";")
    #supply_previous = init_supply
    for index, row in df.iterrows():
        supply = row['total_supply_lag']
        type = row['type']
        unit_building = row['on_building']
        unit_supply = row['supply']
   
        unit_name = row['unit_name']

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
            build_order.append((cum_supply_at_least(supply), train_unit(UnitTypeId[unit_name], on_building = UnitTypeId[unit_building.upper()], increased_supply = unit_supply)))
        elif(type == "Upgrade"):
            # ignore upgrades e.g. spray
            # TODO check if it works
            try:
                build_order.append((supply_at_least(supply), train_unit(UpgradeId[unit_name], on_building = UnitTypeId[unit_building.upper()])))
            except (NameError, KeyError):
                print("Error appending Upgrade {0}".format(unit_name))
                pass
            except AttributeError:
                print("Error appending Upgrade {0}, building {1} not found".format(unit_name, unit_building))
                pass

        #supply_previous = supply
            
    return build_order
        
