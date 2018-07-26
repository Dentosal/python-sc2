from bot_ai_extended import *

def get_test_buildorder(build_order_extended): 
    build_order_basic = [
        (supply_at_least(14), add_gas()),
        (supply_at_least(14), add_gas())
    ]

    build_order_basic.extend(build_order_extended)
    return build_order_basic

   
def get_test_buildorder_research():
    build_order_research = [
        (supply_at_least(14), construct(UnitTypeId.ENGINEERINGBAY)),
        ((all_of(supply_at_least(16), unit_count_at_least_completed(UnitTypeId.ENGINEERINGBAY, 1)), 
                                research(AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYARMORLEVEL1, on_building = UnitTypeId.ENGINEERINGBAY)))
    ]
    return get_test_buildorder(build_order_research)

def get_test_buildorder_research_tiwl():
    build_order_research = [        
        (supply_at_least(14), research(AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1, on_building = UnitTypeId.ENGINEERINGBAY)),
        (supply_at_least(15), research(AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL2, on_building = UnitTypeId.ENGINEERINGBAY))
    ]
    return get_test_buildorder(build_order_research)





def get_test_buildorder_build_required_viking():
    build_order_required = [
        (supply_at_least(13), train_unit(UnitTypeId.VIKINGFIGHTER, on_building = UnitTypeId.STARPORT, repeatable = True))  
    ]
    return get_test_buildorder(build_order_required)

def get_test_buildorder_build_required_thor():
    build_order_required = [
        (supply_at_least(13), train_unit(UnitTypeId.THOR, on_building = UnitTypeId.FACTORY, repeatable = True))  
    ]
    return get_test_buildorder(build_order_required)




def get_test_buildorder_build_BFS():
    build_order_required = [
        (supply_at_least(13), construct(UnitTypeId.BARRACKS)),
        (supply_at_least(14), construct(UnitTypeId.FACTORY)),
        (supply_at_least(15), construct(UnitTypeId.STARPORT))  
    ]
    return get_test_buildorder(build_order_required)


class Strategy_Test(Bot_AI_Extended):
    """Only for testing purposes"""

    def __init__(self):
        init_loggers()
        build_order = get_test_buildorder_research_tiwl() #   get_test_buildorder_build_required_thor() #get_test_buildorder_build_BFS() # get_test_buildorder([])
        self.attack = False
        self.defending = False
        self.researched = []
        self.build_order = BuildOrder(self, build_order, worker_count=init_worker_count) 
        self.first_base = None
        self.path = ""
        self.enemy_base = None

        logger = logging.getLogger("sc2.strategy")
        logger.setLevel(logging.DEBUG)

        self.logger = logger


def main():
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, Strategy_Test()),
        Computer(Race.Terran, Difficulty.Medium)
    ], realtime=False)


if __name__ == '__main__':
    main()




