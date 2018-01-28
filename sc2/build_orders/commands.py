from sc2 import ActionResult, Race
from sc2.constants import *


class Command(object):
    def __init__(self, action, repeatable=False, priority=False):
        self.action = action
        self.is_done = False
        self.is_repeatable = repeatable
        self.is_priority = priority

    async def execute(self, bot, state):
        e = await self.action(bot, state)
        if not e and not self.is_repeatable:
            self.is_done = True

        return e

    def allow_repeat(self):
        self.is_repeatable = True
        self.is_done = False
        return self


def expand(prioritize=False, repeatable=True):
    async def do_expand(bot, state):
        building = bot.basic_townhall_type
        can_afford = bot.can_afford(building)
        if can_afford:
            return await bot.expand_now(building=building)
        else:
            return can_afford.action_result

    return Command(do_expand, priority=prioritize, repeatable=repeatable)


def train(unit, on_building, prioritize=False, repeatable=False):
    async def do_train(bot, state):
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

    return Command(do_train, priority=prioritize, repeatable=repeatable)


def morph(unit, prioritize=False, repeatable=False):
    async def do_morph(bot, state):
        larvae = bot.units(UnitTypeId.LARVA)
        if larvae.exists:
            selected = larvae.first
            can_afford = bot.can_afford(unit)
            if can_afford:
                print("Morph {}".format(unit))
                return await bot.do(selected.train(unit))
            else:
                return can_afford.action_result
        else:
            return ActionResult.Error

    return Command(do_morph, priority=prioritize, repeatable=repeatable)


def build(building, around_building=None, placement=None, prioritize=True, repeatable=False):
    async def do_build(bot, state):
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

    return Command(do_build, priority=prioritize, repeatable=repeatable)


def add_supply(prioritize=True, repeatable=False):
    async def supply_spec(bot, state):
        can_afford = bot.can_afford(bot.supply_type)
        if can_afford:
            if bot.race == Race.Zerg:
                return await morph(bot.supply_type).execute(bot, state)
            else:
                return await build(bot.supply_type).execute(bot, state)
        else:
            return can_afford.action_result

    return Command(supply_spec, priority=prioritize, repeatable=repeatable)


def add_gas(prioritize=True, repeatable=False):
    async def do_add_gas(bot, state):
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

    return Command(do_add_gas, priority=prioritize, repeatable=repeatable)
