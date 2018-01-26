class BuildOrder(object):
    def __init__(self, bot, build):
        self.build = build
        self.bot = bot
        self.next_execution = 0

    async def execute_build(self, state):
        for index, item in enumerate(self.build):
            if index > self.next_execution:
                return None

            condition, intent = item
            action, intended_unit = intent
            condition = item[0] if item[0] else always_true
            if condition(self.bot, state) and self.bot.can_afford(intended_unit):
                self.next_execution = index + 1
                return await action(self.bot, state)


def train(unit, on_building):
    async def train_spec(bot, state):
        buildings = bot.units(on_building).ready.noqueue
        if buildings.exists:
            selected = buildings.first
            print("Training {}".format(unit))
            return await bot.do(selected.train(unit))
        else:
            return None

    return train_spec, unit


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
        print("Building {}".format(building))
        return await bot.build(building, near=location)

    return build_spec, building


def all_of(*args):
    def condition(bot, state):
        return all(map(lambda a: a(bot, state), args))

    return condition


def any_of(*args):
    def condition(bot, state):
        return all(any(lambda a: a(bot, state), args))

    return condition


def always_true(bot, state):
    return True


def supply_is(s):
    def condition(bot, state):
        return bot.supply_used == s
    condition.__str__()
    return condition


def gas_at_least(s):
    def condition(bot, state):
        return bot.vespene >= s

    return condition


def minerals_at_least(s):
    def condition(bot, state):
        return bot.minerals >= s

    return condition