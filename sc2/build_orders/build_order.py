from sc2 import Race, race_worker, ActionResult, race_townhalls
from sc2.build_orders.commands import train_unit, add_supply, morph, build_required
from sc2.state_conditions.conditions import always_true, unit_count_at_least
from sc2.constants import *
from util import measure_runtime

class BuildOrder(object):
    def __init__(self, bot, build, worker_count=0, auto_add_supply=True):
        self.build = build
        self.bot = bot
        self.worker_count = worker_count
        self.auto_add_supply = auto_add_supply
        self.bot.cum_supply = init_supply
         
   
    # HS adapted + moved
    @measure_runtime
    async def increase_workers(self):
        """Increase number of workers, if below target amount"""
        bot = self.bot
        if bot.workers.amount < self.worker_count:
            if bot.race == Race.Zerg:
                return await morph(race_worker[Race.Zerg], increased_supply = worker_supply).execute(bot)
            else:
                return await train_unit(race_worker[bot.race], race_townhalls[self.bot.race], increased_supply = worker_supply).execute(bot)

            
    # HS adapted + moved
    @measure_runtime
    async def increase_supply(self):   
        """Increase supply if close to supply cap"""
        max_supply_cap = 200
        bot = self.bot
        # bot.supply_left <= ((bot.supply_cap+40) / 40)
        if bot.supply_left <= bot.supply_cap * 0.1 + 1 and not bot.already_pending(bot.supply_type) \
                and self.auto_add_supply and bot.supply_cap < max_supply_cap:
            return await add_supply().execute(bot)

    # HS adapted
    @measure_runtime
    async def execute_build(self):
        bot = self.bot
        
        for index, item in enumerate(self.build):
            condition, command = item
            
            condition = item[0] if item[0] else always_true
            if not command.is_done and condition(bot):

                if command.requires is not None: 
                    await build_required(self, bot, command.requires)

                if command.requires_2nd is not None:
                    await build_required(self, bot, command.requires_2nd)
                                 
                e = await command.execute(bot)
                
                if command.is_done: 
                    return e
                
                else:
                    # Save up to be able to do this command and hold worker creation.
                    if command.is_priority and e == ActionResult.NotEnoughMinerals:
                        return e

                    if e == ActionResult.NotEnoughFood and self.auto_add_supply \
                            and not bot.already_pending(bot.supply_type):
                        return await add_supply().execute(bot)
                    continue

        return None
