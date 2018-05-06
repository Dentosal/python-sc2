import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.build_orders.build_order import BuildOrder, train_unit
from sc2.build_orders.commands import construct, expand, add_supply, add_gas
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.state_conditions.conditions import all_of, supply_at_least, minerals_at_least, unit_count

from abc import ABCMeta, abstractmethod, abstractproperty

from strategy_util import *
from time import gmtime, strftime



class Terran_Bot_Buildorder(sc2.BotAI):

    

    def get_researched_upgrades():
        ''' To override '''
        pass


    # TODO dict with upgrades pending or finished
    '''
        def can_research(self, upgrade_id, on_building):
            if isinstance(upgrade_id, UpgradeId) and self.can_afford(upgrade_id) and self.units(on_building).ready.exists and not upgrade_id in get_researched_upgrades():
                upgrader = self.units(on_building).ready.first
                await self.do(upgrader(upgrade_id))
                #self.cloak_started = True
    '''   

    def __init__(self, map_name, self_race, enemy_race):

        hash = "1cc609b79314bee713eb2e3708c3ae4d2a03762c"#"90145ee27487043a70b38e4346100dd882197036"
        
        folder = folder_buildorder + self_race + race_bot_separator + enemy_race + ending_folder + map_name + ending_folder
        path = folder + hash + ending_csv
        
        build_order = init_build_order(path)
        self.attack = False
        self.build_order = BuildOrder(self, build_order, worker_count=init_worker_count)
       
       
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_order.execute_build()
        
        # to avoid conflicts with build order
        #if self.supply_left < 3 and  self.supply_used >30:
        #    add_supply()
          
        # TODO research in build order

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
            
# TODO
def get_units_attack(self):
    self.units

def main():
    map_name = "Catalyst LE"
    self_race = Race.Terran
    enemy_race = Race.Terran
    time = strftime("%Y-%m-%d-%H:%M:%S", gmtime())
    output_replay = map_name +  race_to_string(self_race) + race_bot_separator + race_to_string(enemy_race) 

    run_game(maps.get(map_name), [
        Bot(self_race, Terran_Bot_Buildorder(map_name, race_to_string(self_race), race_to_string(enemy_race))),
        Computer(enemy_race, Difficulty.Easy)
    ], realtime=False, save_replay_as= output_replay)

if __name__ == '__main__':
    main()





