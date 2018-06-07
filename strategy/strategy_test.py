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
            (supply_at_least(15), train_unit(UnitTypeId.VIKINGFIGHTER, on_building = UnitTypeId.STARPORT))         
        ]
        self.attack = False
        self.defending = False
        self.build_order = BuildOrder(self, build_order, worker_count=init_worker_count) 
       
 
def main():
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, Strategy_Test()),
        Computer(Race.Random, Difficulty.Easy)
    ], realtime=False)

if __name__ == '__main__':
    main()




