
from bot_ai_extended import *

class Terran_Bot_Buildorder(Bot_AI_Extended):



    # TODO list with upgrades pending or finished
    '''
        def can_research(self, upgrade_id, on_building):
            if isinstance(upgrade_id, UpgradeId) and self.can_afford(upgrade_id) and self.units(on_building).ready.exists and not upgrade_id in get_researched_upgrades():
                upgrader = self.units(on_building).ready.first
                await self.do(upgrader(upgrade_id))
                #self.cloak_started = True
    '''   

    
       
       
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_order.execute_build()
        
        # to avoid conflicts with build order
        #if self.supply_left < 3 and  self.supply_used >30:
        #    add_supply()
          
        # TODO research in build order

        # TODO can be improved significantly --> e.g. superclass units without SCV
        units_military = get_units_military(self)



        # TODO attack as group, or solution as in proxy_ray.py???
        if len(units_military)  >= 5 or self.attack:
            self.attack = True
            for unit in  filter(lambda u: u.is_idle, units_military):
                await self.do(unit.attack(self.enemy_start_locations[0]))
                if self.known_enemy_structures.exists:
                    enemy = self.known_enemy_structures.first
                    await self.do(unit.attack(enemy.position.to2, queue=True))
           
            return
            







