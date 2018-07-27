from bot_ai_extended import *

class Strategy_Test(Bot_AI_Extended):
    """Only for testing purposes"""

    def get_buildorder(self, path, logger):
        """Overrides Bot_AI_Extended method, change strategy here"""
        return self.get_build_order_111expand()  #self.get_test_buildorder_build_BFS()

    def get_test_buildorder(self, build_order_extended): 
        """Basic buildorder as basis"""

        build_order_basic = [
            (supply_at_least(14), add_gas()),
            (supply_at_least(14), add_gas())
        ]

        build_order_basic.extend(build_order_extended)
        return build_order_basic

    def get_test_buildorder_research(self):
        """Testing research functionality"""
        build_order_research = [
            (supply_at_least(14), construct(UnitTypeId.ENGINEERINGBAY)),
            ((all_of(supply_at_least(16), unit_count_at_least_completed(UnitTypeId.ENGINEERINGBAY, 1)), 
                                    research(AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYARMORLEVEL1, on_building = UnitTypeId.ENGINEERINGBAY)))
        ]
        return self.get_test_buildorder(build_order_research)

    def get_test_buildorder_research_tiwl(self):
        """Testing research build required functionality"""
        build_order_research = [        
            (supply_at_least(14), research(AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1, on_building = UnitTypeId.ENGINEERINGBAY)),
            (supply_at_least(15), research(AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL2, on_building = UnitTypeId.ENGINEERINGBAY))
        ]
        return self.get_test_buildorder(build_order_research)

    def get_test_buildorder_build_required_viking(self):
        """Testing  build required functionality"""
        build_order_required = [
            (supply_at_least(13), train_unit(UnitTypeId.VIKINGFIGHTER, on_building = UnitTypeId.STARPORT, repeatable = True))  
        ]
        return self.get_test_buildorder(build_order_required)

    def get_test_buildorder_build_required_thor(self):
        """Testing  build (2nd) required functionality"""
        build_order_required = [
            (supply_at_least(13), train_unit(UnitTypeId.THOR, on_building = UnitTypeId.FACTORY, repeatable = True))  
        ]
        return self.get_test_buildorder(build_order_required)

    def get_test_buildorder_build_BFS(self):
        """Short sample build_order"""
        build_order = [
            (supply_at_least(13), construct(UnitTypeId.BARRACKS)),
            (supply_at_least(14), construct(UnitTypeId.FACTORY)),
            (supply_at_least(15), construct(UnitTypeId.STARPORT))  
        ]
        return self.get_test_buildorder(build_order)

    def get_build_order_111expand(self):
        """Slightly modified 111 expand strategy based on https://liquipedia.net/starcraft2/111_Expand"""
        build_order = [           
            (supply_at_least(15), add_gas()),
            (supply_at_least(16), construct(UnitTypeId.BARRACKS, prioritize=True)),
            (all_of(supply_at_least(19), unit_count(UnitTypeId.BARRACKS, 1, include_pending=False)), train_unit(UnitTypeId.ORBITALCOMMAND, on_building = UnitTypeId.COMMANDCENTER, increased_supply = 1)),
            (supply_at_least(19), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(20), construct(UnitTypeId.FACTORY)),
            (supply_at_least(20), add_gas()),
            (all_of(supply_at_least(20), unit_count(UnitTypeId.MARINE, 1, include_pending=False)), train_unit(UnitTypeId.REAPER, on_building = UnitTypeId.BARRACKS, increased_supply = 1)),
            (all_of(supply_at_least(24), unit_count(UnitTypeId.FACTORY, 1, include_pending=False)), train_unit(UnitTypeId.HELLION, on_building = UnitTypeId.FACTORY, increased_supply = 2)),
            (supply_at_least(24), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS, increased_supply = 1)),
            (all_of(supply_at_least(26), unit_count(UnitTypeId.FACTORY, 1, include_pending=False)), construct(UnitTypeId.STARPORT, prioritize=True)),
            (supply_at_least(26), train_unit(UnitTypeId.HELLION, on_building=UnitTypeId.FACTORY, increased_supply = 2)),
            (supply_at_least(27), train_unit(UnitTypeId.HELLION, on_building=UnitTypeId.FACTORY, increased_supply = 2)),
            (all_of(supply_at_least(31), unit_count(UnitTypeId.STARPORT, 1, include_pending=False)), train_unit(UnitTypeId.STARPORTTECHLAB, on_building = UnitTypeId.STARPORT)),
            (all_of(supply_at_least(32), unit_count(UnitTypeId.STARPORTTECHLAB, 1, include_pending=False)), train_unit(UnitTypeId.BANSHEE, on_building = UnitTypeId.STARPORT)), 
            (all_of(supply_at_least(32), unit_count(UnitTypeId.STARPORTTECHLAB, 1, include_pending=False)), research(AbilityId.RESEARCH_BANSHEECLOAKINGFIELD, on_building = UnitTypeId.STARPORTTECHLAB)),
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1, include_pending=False), expand(prioritize=True, repeatable=False)),           
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS, repeatable=True, increased_supply = 1)),
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1), train_unit(UnitTypeId.BANSHEE, on_building=UnitTypeId.STARPORT, repeatable=True, increased_supply = 2)),
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1), train_unit(UnitTypeId.HELLION, on_building=UnitTypeId.FACTORY, repeatable=True, increased_supply = 2))
        ]
        return build_order
    

def main():
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, Strategy_Test()),
        Computer(Race.Terran, Difficulty.Hard)
    ], realtime=False)


if __name__ == '__main__':
    main()




