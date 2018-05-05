from sc2 import Race, race_worker, ActionResult, race_townhalls
from sc2.build_orders.commands import add_supply, morph, train_unit
from sc2.state_conditions.conditions import always_true


class BuildOrder(object):
    def __init__(self, bot, build, worker_count=0, auto_add_supply=True):
        self.build = build
        self.bot = bot
        self.worker_count = worker_count
        self.auto_add_supply = auto_add_supply

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

                if command.increase_workers > 0:            
                    # Increase worker count due to expansion
                    self.worker_count = self.worker_count + command.increase_workers

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

        if bot.workers.amount < self.worker_count:
            if bot.race == Race.Zerg:
                return await morph(race_worker[Race.Zerg]).execute(bot)
            else:
                return await train_unit(race_worker[bot.race], race_townhalls[self.bot.race]).execute(bot)
        return None
