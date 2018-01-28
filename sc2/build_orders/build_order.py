from sc2 import Race, race_worker, ActionResult, race_townhalls
from sc2.ids.unit_typeid import UnitTypeId
from sc2.state_conditions.conditions import always_true


class Intent(object):
    def __init__(self, action):
        self.action = action
        self.done = False
        self.infinite = False

    async def execute(self, bot, state):
        e = await self.action(bot, state)
        if not e and not self.infinite:
            self.done = True

        return e

    def keep_going(self):
        self.infinite = True
        return self

    @property
    def is_done(self):
        return self.done


class BuildOrder(object):
    def __init__(self, bot, build, worker_count=0, auto_add_supply=True):
        self.build = build
        self.bot = bot
        self.worker_count = worker_count
        self.auto_add_supply = auto_add_supply

    async def execute_build(self, state):
        bot = self.bot
        if bot.supply_left <= (bot.supply_cap / 50) and not bot.already_pending(bot.supply_type)\
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


def expand():
    async def expand_spec(bot, state):
        building = bot.basic_townhall_type
        if bot.can_afford(building):
            return await bot.expand_now(building=building)
        else:
            return ActionResult.Error

    return Intent(expand_spec)


def train(unit, on_building):
    async def train_spec(bot, state):
        buildings = bot.units(on_building).ready.noqueue
        if buildings.exists and bot.can_afford(unit):
            selected = buildings.first
            print("Training {}".format(unit))
            return await bot.do(selected.train(unit))
        else:
            return ActionResult.Error

    return Intent(train_spec)


def morph(unit):
    async def train_spec(bot, state):
        larvae = bot.units(UnitTypeId.LARVA)
        if larvae.exists and bot.can_afford(unit):
            selected = larvae.first
            print("Morph {}".format(unit))
            return await bot.do(selected.train(unit))
        else:
            return ActionResult.Error

    return Intent(train_spec)


def build(building, around_building=None, placement=None):
    async def build_spec(bot, state):
        if not around_building:
            around = bot.townhalls.first
        else:
            around = around_building(bot, state)

        if not placement:
            location = around.position.towards(bot.game_info.map_center, 5)
        else:
            location = placement
        if bot.can_afford(building):
            print("Building {}".format(building))
            return await bot.build(building, near=location)
        else:
            return ActionResult.Error

    return Intent(build_spec)


def add_supply():
    async def supply_spec(bot, state):
        if bot.can_afford(bot.supply_type):
            if bot.race == Race.Zerg:
                return await morph(bot.supply_type).execute(bot, state)
            else:
                return await build(bot.supply_type).execute(bot, state)
        else:
            return ActionResult.Error

    return Intent(supply_spec)


def add_gas():
    async def add_gas_spec(bot, state):
        for th in bot.townhalls:
            for nexus in bot.units(th.type_id).ready:
                vgs = state.vespene_geyser.closer_than(20.0, nexus)
                for vg in vgs:
                    if not bot.can_afford(UnitTypeId.EXTRACTOR):
                        break

                    worker = bot.select_build_worker(vg.position)
                    if worker is None:
                        break

                    if not bot.units(UnitTypeId.EXTRACTOR).closer_than(1.0, vg).exists:
                        return await bot.do(worker.build(UnitTypeId.EXTRACTOR, vg))
        return ActionResult.Error

    return Intent(add_gas_spec)
