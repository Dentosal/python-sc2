from sc2 import Race, race_worker, ActionResult, race_townhalls
from sc2.build_orders.commands import add_supply, morph, train_unit, construct
from sc2.state_conditions.conditions import always_true, unit_count_at_least
from sc2.constants import *

class BuildOrder(object):
    def __init__(self, bot, build, worker_count=0, auto_add_supply=True):
        self.build = build
        self.bot = bot
        self.worker_count = worker_count
        self.auto_add_supply = auto_add_supply
        self.bot.cum_supply = init_supply
        

    async def execute_build(self):
        bot = self.bot
        if bot.supply_left <= ((bot.supply_cap+50) / 50) and not bot.already_pending(bot.supply_type) \
                and self.auto_add_supply:
            return await add_supply().execute(bot)

        

        for index, item in enumerate(self.build):
            condition, command = item
            condition = item[0] if item[0] else always_true
            if condition(bot) and not command.is_done:
                e = await command.execute(bot)


                if command.is_done:
                    return e

                elif e == ActionResult.NotSupported and command.requires is not None:
                    # required building currently constructing
                    require_condition = unit_count_at_least(command.requires, 1, True)
                    if require_condition(bot):       
                        return e
                    else:
                        # CHECK build new building
                        print("Build new building {0} due to requirements".format(command.requires))
                        await construct(command.requires).execute(bot)
                        return e
                    continue
               #     
               #     if command.requires and not bot.already_pending(command.requires): 
               #         print("BUILDING required")
               #     elif command.requires and not bot.already_pending(command.requires):
               #          print("Required BUILDING currently building")
                else:
                    # Save up to be able to do this command and hold worker creation.
                    if command.is_priority and e == ActionResult.NotEnoughMinerals:
                        return e

                    if e == ActionResult.NotEnoughFood and self.auto_add_supply \
                            and not bot.already_pending(bot.supply_type):
                        return await add_supply().execute(bot)
                    continue

        if bot.workers.amount < self.worker_count:
            if bot.race == Race.Zerg:
                return await morph(race_worker[Race.Zerg], increased_supply = worker_supply).execute(bot)
            else:
                return await train_unit(race_worker[bot.race], race_townhalls[self.bot.race], increased_supply = worker_supply).execute(bot)

            
        

        return None
