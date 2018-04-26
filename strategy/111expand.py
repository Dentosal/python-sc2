import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.build_orders.build_order import BuildOrder, train_unit
from sc2.build_orders.commands import construct, expand, add_supply, add_gas
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.state_conditions.conditions import all_of, supply_at_least, minerals_at_least, unit_count


class Strategy_111Expand(sc2.BotAI):

   

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
        self.build_order = BuildOrder(self, build_order, worker_count=21) # 20 also vespene gas, 16 only mineral, 21 as reserve for building units
       
        

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

        # TODO can be improved significantly --> e.g. superclass units without SCV
        if self.units(UnitTypeId.MARINE).amount + self.units(UnitTypeId.HELLION).amount + self.units(UnitTypeId.BANSHEE).amount  >= 15 or self.attack:
            self.attack = True
            for unit in self.units(UnitTypeId.MARINE).idle:
                await self.do(unit.attack(self.enemy_start_locations[0]))
                if self.known_enemy_structures.exists:
                    enemy = self.known_enemy_structures.first
                    await self.do(unit.attack(enemy.position.to2, queue=True))
            
            for unit in self.units(UnitTypeId.HELLION).idle:
                await self.do(unit.attack(self.enemy_start_locations[0]))
                if self.known_enemy_structures.exists:
                    enemy = self.known_enemy_structures.first
                    await self.do(unit.attack(enemy.position.to2, queue=True))
            
            for unit in self.units(UnitTypeId.BANSHEE).idle:
                await self.do(unit.attack(self.enemy_start_locations[0]))
                if self.known_enemy_structures.exists:
                    enemy = self.known_enemy_structures.first
                    await self.do(unit.attack(enemy.position.to2, queue=True))
            return
            


def main():
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, Strategy_111Expand()),
        # Bot(Race.Terran, TerranBuildOrderBot()),
        Computer(Race.Random, Difficulty.Easy)
    ], realtime=False, save_replay_as="111ExpandVsEasy.SC2Replay")

if __name__ == '__main__':
    main()




