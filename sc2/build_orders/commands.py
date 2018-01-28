from sc2 import ActionResult, Race
from sc2.constants import *


class Command(object):
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


def expand():
    async def expand_spec(bot, state):
        building = bot.basic_townhall_type
        can_afford = bot.can_afford(building)
        if can_afford:
            return await bot.expand_now(building=building)
        else:
            return can_afford.action_result

    return Command(expand_spec)


def train(unit, on_building):
    async def train_spec(bot, state):
        buildings = bot.units(on_building).ready.noqueue
        if buildings.exists:
            selected = buildings.first
            can_afford = bot.can_afford(unit)
            if can_afford:
                print("Training {}".format(unit))
                return await bot.do(selected.train(unit))
            else:
                return can_afford.action_result
        else:
            return ActionResult.Error

    return Command(train_spec)


def morph(unit):
    async def train_spec(bot, state):
        larvae = bot.units(UnitTypeId.LARVA)
        if larvae.exists and bot.can_afford(unit):
            selected = larvae.first
            can_afford = bot.can_afford(unit)
            if can_afford:
                print("Morph {}".format(unit))
                return await bot.do(selected.train(unit))
            else:
                return can_afford.action_result
        else:
            return ActionResult.Error

    return Command(train_spec)


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

        can_afford = bot.can_afford(building)
        if can_afford:
            print("Building {}".format(building))
            return await bot.build(building, near=location)
        else:
            return can_afford.action_result

    return Command(build_spec)


def add_supply():
    async def supply_spec(bot, state):
        can_afford = bot.can_afford(bot.supply_type)
        if can_afford:
            if bot.race == Race.Zerg:
                return await morph(bot.supply_type).execute(bot, state)
            else:
                return await build(bot.supply_type).execute(bot, state)
        else:
            return can_afford.action_result

    return Command(supply_spec)


def add_gas():
    async def add_gas_spec(bot, state):
        can_afford = bot.can_afford(bot.geyser_type)
        if not can_afford:
            return can_afford.action_result

        owned_expansions = bot.owned_expansions
        for location, th in owned_expansions.items():
            vgs = state.vespene_geyser.closer_than(20.0, th)
            for vg in vgs:
                worker = bot.select_build_worker(vg.position)
                if worker is None:
                    break

                if not bot.units(bot.geyser_type).closer_than(1.0, vg).exists:
                    return await bot.do(worker.build(bot.geyser_type, vg))

        return ActionResult.Error

    return Command(add_gas_spec)
