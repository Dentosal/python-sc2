from sc2 import Race, race_worker, ActionResult, race_townhalls
from sc2.build_orders.commands import add_supply, morph, train
from sc2.state_conditions.conditions import always_true


class BuildOrder(object):
    def __init__(self, bot, build, worker_count=0, auto_add_supply=True):
        self.build = build
        self.bot = bot
        self.worker_count = worker_count
        self.auto_add_supply = auto_add_supply

    async def execute_build(self, state):
        bot = self.bot
        if bot.supply_left <= (bot.supply_cap / 50) and not bot.already_pending(bot.supply_type) \
                and self.auto_add_supply:
            return await add_supply().execute(bot, state)

        for index, item in enumerate(self.build):
            condition, intent = item
            condition = item[0] if item[0] else always_true
            if condition(bot, state) and not intent.is_done:
                e = await intent.execute(bot, state)
                if intent.is_done:
                    return e
                else:
                    if e == ActionResult.NotEnoughFood and self.auto_add_supply \
                            and not bot.already_pending(bot.supply_type):
                        return await add_supply().execute(bot, state)
                    continue

        if bot.workers.amount < self.worker_count:
            if bot.race == Race.Zerg:
                return await morph(race_worker[Race.Zerg]).execute(bot, state)
            else:
                return await train(race_worker[bot.race], race_townhalls[self.bot.race]).execute(bot, state)
        return None