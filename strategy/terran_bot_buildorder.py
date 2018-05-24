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


        if iteration % gameloops_check_frequency*2 == 0: 
            await auto_build(self)
        
        if iteration % gameloops_check_frequency == 0:
            await auto_attack(self)
             
           
            







