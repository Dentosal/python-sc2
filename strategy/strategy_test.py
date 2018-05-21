import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.build_orders.build_order import BuildOrder, train_unit
from sc2.build_orders.commands import construct, expand, add_supply, add_gas
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.state_conditions.conditions import all_of, supply_at_least, minerals_at_least, unit_count
from bot_ai_extended import *

class Strategy_Test(Bot_AI_Extended):
    """Only for testing purposes"""
   
    def __init__(self):
        build_order = [
            #(supply_at_least(14), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(14), add_gas()),
            (supply_at_least(14), add_gas()),
            #(supply_at_least(14), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            #(supply_at_least(15), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            #(supply_at_least(15), train_unit(UnitTypeId.HELLION, on_building=UnitTypeId.FACTORY)),
            #(supply_at_least(20), train_unit(UnitTypeId.STARPORTTECHLAB, on_building = UnitTypeId.STARPORT)), 
            #(supply_at_least(15), train_unit(UnitTypeId.VIKINGFIGHTER, on_building = UnitTypeId.STARPORT))         
        ]
        self.attack = False
        self.build_order = BuildOrder(self, build_order, worker_count=init_worker_count) 
       
      


        
            


def main():
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, Strategy_Test()),
        Computer(Race.Random, Difficulty.Easy)
    ], realtime=False)

if __name__ == '__main__':
    main()




