import csv
import pandas as pd
from sc2.build_orders.build_order import train_unit
from sc2.state_conditions.conditions import  supply_at_least
from sc2.build_orders.commands import construct, expand, add_supply, add_gas
from sc2.constants import *
from sc2.data import *

import re

def init_build_order(path):

    build_order = []
    df = pd.read_csv(path, sep=";")

    for index, row in df.iterrows():
        supply = row['total_supply_lag']
        type = row['type']
        unit_building = row['on_building']

   
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
                build_order.append((supply_at_least(supply), add_gas()))
            elif(unit_name in main_buildings): # race_basic_townhalls
                build_order.append((supply_at_least(supply), expand(repeatable=False)))
            else:
                build_order.append((supply_at_least(supply), construct(UnitTypeId[unit_name])))
        elif(type == "Unit"):
            build_order.append((supply_at_least(supply), train_unit(UnitTypeId[unit_name], on_building = UnitTypeId[unit_building.upper()])))
        #elif(type == "Upgrade"):
        #    build_order.append((supply_at_least(supply), train_unit(UpgradeId[unit_name], on_building = UnitTypeId[unit_building.upper()])))
            
    return build_order
        
        #elif(row['type'] == "Upgrade"):
        
        #build_order.append((supply_at_least(row['total_supply_lag']), )
        #print( + row['unit_name'] +  row['type'])

   
    #df
    #with open(path, newline='') as csvfile:
    #    csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
    #    for row in csvreader:
    #        build_order.append(())
    #        print(', '.join(row))
