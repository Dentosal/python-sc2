from bot_ai_extended import *


class Strategy_111Expand(Bot_AI_Extended):

   
    def __init__(self):
        
        self.cloak_started = False

        build_order = [

            # slightly modified
           
            (supply_at_least(14), add_supply(prioritize=True)),
            (supply_at_least(15), add_gas()),
            (supply_at_least(16), construct(UnitTypeId.BARRACKS, prioritize=True)),
            (all_of(supply_at_least(19), unit_count(UnitTypeId.BARRACKS, 1, include_pending=False)), train_unit(UnitTypeId.ORBITALCOMMAND, on_building = UnitTypeId.COMMANDCENTER)),
            (supply_at_least(19), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(20), construct(UnitTypeId.FACTORY)),
            (supply_at_least(20), add_supply(prioritize=True)),
            (supply_at_least(20), add_gas()),
           # (supply_at_least(20), expand(prioritize=True)), # test
            (all_of(supply_at_least(20), unit_count(UnitTypeId.MARINE, 1, include_pending=False)), train_unit(UnitTypeId.REAPER, on_building = UnitTypeId.BARRACKS)),
            (all_of(supply_at_least(24), unit_count(UnitTypeId.FACTORY, 1, include_pending=False)), train_unit(UnitTypeId.HELLION, on_building = UnitTypeId.FACTORY)),
            (supply_at_least(24), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)), # 1 Supply Missing
            (all_of(supply_at_least(26), unit_count(UnitTypeId.FACTORY, 1, include_pending=False)), construct(UnitTypeId.STARPORT, prioritize=True)),
            (supply_at_least(26), train_unit(UnitTypeId.HELLION, on_building=UnitTypeId.FACTORY)), # 2 Supply Missing
            (supply_at_least(27), add_supply(prioritize=True)),
            (supply_at_least(27), train_unit(UnitTypeId.HELLION, on_building=UnitTypeId.FACTORY)),
            (supply_at_least(31), add_supply(prioritize=True)),
            (all_of(supply_at_least(31), unit_count(UnitTypeId.STARPORT, 1, include_pending=False)), train_unit(UnitTypeId.STARPORTTECHLAB, on_building = UnitTypeId.STARPORT)),
            (all_of(supply_at_least(32), unit_count(UnitTypeId.STARPORTTECHLAB, 1, include_pending=False)), train_unit(UnitTypeId.BANSHEE, on_building = UnitTypeId.STARPORT)), # eigentlich TECHLAB bei unitcount
            # TODO  (all_of(supply_at_least(32), unit_count(UnitTypeId.TECHLAB, 1, include_pending=False)), train_unit(UnitTypeId.BANSHEECLOAK, on_building = UnitTypeId.STARPORT),
            
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1, include_pending=False), expand(prioritize=True, repeatable=False)), # eigentlich 36
           # (unit_count(UnitTypeId.STARPORTTECHLAB, 1, include_pending=False), research(UnitTypeId.STARPORTTECHLAB, AbilityId.RESEARCH_BANSHEECLOAKINGFIELD)),
            
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS, repeatable=True)),
            #((supply_at_least(36), unit_count(UnitTypeId.BARRACKS, 5, include_pending=True)), add_supply(prioritize=True)),
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1), train_unit(UnitTypeId.BANSHEE, on_building=UnitTypeId.STARPORT, repeatable=True)),
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1), train_unit(UnitTypeId.HELLION, on_building=UnitTypeId.FACTORY, repeatable=True))
         
        ]
        self.attack = False
        self.build_order = BuildOrder(self, build_order, worker_count=init_worker_count)
       
        

    #async def expand(self):
    #    if self.units(UnitTypeId.COMMANDCENTER).amount < 3 and self.can_afford(UnitTypeId.COMMANDCENTER) and self.supply_used >= 36:
    #        await self.expand_now()

    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_order.execute_build()
        
        # to avoid conflicts with build order
        if self.supply_left < 3 and  self.supply_used >30:
            add_supply()
          
        # TODO research in build order
        if not self.cloak_started and self.units(STARPORTTECHLAB).ready.exists and self.can_afford(RESEARCH_BANSHEECLOAKINGFIELD):
            upgrader = self.units(STARPORTTECHLAB).ready.first
            await self.do(upgrader(RESEARCH_BANSHEECLOAKINGFIELD))
            self.cloak_started = True

        if iteration % gameloops_check_frequency == 0:
            await auto_attack(self)
            


def main():
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, Strategy_111Expand()),
        # Bot(Race.Terran, TerranBuildOrderBot()),
        Computer(Race.Random, Difficulty.Easy)
    ], realtime=False, save_replay_as="111ExpandVsEasy.SC2Replay")

if __name__ == '__main__':
    main()




