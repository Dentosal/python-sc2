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
    def __init__(self, bot, build, worker_count=0):
        self.build = build
        self.bot = bot
        self.worker_count = worker_count

    async def execute_build(self, state):
        for index, item in enumerate(self.build):
            condition, intent = item
            condition = item[0] if item[0] else always_true
            if condition(self.bot, state) and not intent.is_done:
                e = await intent.execute(self.bot, state)
                if intent.is_done:
                    return e
                else:
                    continue

        if self.bot.workers.amount < self.worker_count:
            if self.bot.race == Race.Zerg:
                return await morph(race_worker[Race.Zerg]).execute(self.bot, state)
            else:
                return await train(race_worker[self.bot.race], self.bot.townhalls.ready.random.type_id).execute(self.bot,
                                                                                                         state)
        return None


def expand():
    async def expand_spec(bot, state):
        building = bot.townhalls.first.type_id
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
