from sc2.build_orders.state_conditions import always_true
from sc2.ids.unit_typeid import UnitTypeId


class BuildOrder(object):
    def __init__(self, bot, build):
        self.build = build
        self.bot = bot
        self.next_execution = 0

    async def execute_build(self, state):
        for index, item in enumerate(self.build):
            if index > self.next_execution:
                return None

            condition, action = item
            condition = item[0] if item[0] else always_true
            if condition(self.bot, state):
                print("Executing build order index {}".format(index))
                self.next_execution = index + 1
                print("Next build order index {}".format(self.next_execution))
                return await action(self.bot, state)


def expand():
    async def expand_spec(bot, state):
        building = bot.townhalls.first.type_id
        if bot.can_afford(building):
            return await bot.expand_now(building=building)
        else:
            return None

    return expand_spec


def train(unit, on_building):
    async def train_spec(bot, state):
        buildings = bot.units(on_building).ready.noqueue
        if buildings.exists and bot.can_afford(unit):
            selected = buildings.first
            print("Training {}".format(unit))
            return await bot.do(selected.train(unit))
        else:
            return None

    return train_spec

def morph(unit):
    async def train_spec(bot, state):
        larvae = bot.units(UnitTypeId.LARVA)
        if larvae.exists and bot.can_afford(unit):
            selected = larvae.first
            print("Morph {}".format(unit))
            return await bot.do(selected.train(unit))
        else:
            return None

    return train_spec


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
            return None

    return build_spec
