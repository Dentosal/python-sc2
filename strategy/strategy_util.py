import csv
import pandas as pd
from sc2.build_orders.build_order import *
from sc2.state_conditions.conditions import  supply_at_least, cum_supply_at_least, all_of, unit_count_at_least
from sc2.build_orders.commands import construct, expand, add_supply, add_gas
from sc2.constants import *
from sc2.data import *
import sc2
from sc2 import Race
import re
from random import uniform, randrange

from math import isclose


def can_build(building, unit):
    # TODO check if unit requires addon
    return isclose(building.build_progress, build_progress_completed) and not building.is_enemy and building.noqueue and building.is_idle

# TODO check
def count_units(bot, unit, exclude_pending, exclude_enemy = True):

    count = 0
    for u in bot.units(unit):

        if exclude_enemy and u.is_enemy:
            continue

        if not exclude_pending:
            count += 1
        else:
            if isclose(u.build_progress, build_progress_completed):
                count += 1

    return count
    


def get_random_building_location(bot):
    return bot.townhalls.random.position.towards(bot.game_info.map_center, randrange(5, 20)).random_on_distance(randrange(5, 12))


# TODO attack as group, or solution as in proxy_ray.py???
# TODO for other races
# TODO couldnt it be improved by adding new units automatically
# TODO can be improved significantly --> e.g. superclass units without SCV
def get_units_military(bot):
    units_military = []

    for unit in terran_military_units:
        units_military = units_military + bot.units(unit)
            
    return  units_military



def get_buildorder_hash(path_strategy, method):
    df = pd.read_csv(path_strategy, sep=";", decimal=b',')

    r = uniform(0,1)
    #print(r)

    for index, row in df.iterrows():
        weight = row[method]
        if weight >= r: 
            return row["Hash"]






def init_build_order(path):

    build_order = []
    df = pd.read_csv(path, sep=";")
    #supply_previous = init_supply
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
            # ignore spray
            if(unit_name[0:5] == "SPRAY"):
                continue

    
            # TODO check if it works
            try:
                unit_building = unit_building.upper()
                build_order.append((all_of(supply_at_least(supply), unit_count_at_least(UnitTypeId[unit_building], 1, include_pending=False)), train_unit(UpgradeId[unit_name], on_building = UnitTypeId[unit_building])))
            except (NameError, KeyError):
                print("Error appending Upgrade {0}".format(unit_name))
               # pass
            except AttributeError:
                print("Error appending Upgrade {0}, building {1} not found".format(unit_name, unit_building))
                pass

        #supply_previous = supply
            
    return build_order
        
