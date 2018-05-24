from sc2 import ActionResult, Race
from sc2.constants import *
from sc2.state_conditions.conditions import  unit_count_at_least
#from strategy_util import *

class Command(object):
    def __init__(self, action, repeatable=False, priority=False, increase_workers = 0, increased_supply = 0, requires = None):
        self.action = action
        self.is_done = False
        self.is_repeatable = repeatable
        self.is_priority = priority
        self.increase_workers = increase_workers
        self.increased_supply = increased_supply
        self.requires = requires

    async def execute(self, bot):

        condition = unit_count_at_least(self.requires, 1, True)
        condition_done = unit_count_at_least(self.requires, 1, False)

        #if  self.requires is not None and not condition:

        #    print("Required {0} is not pending. Therefore, schedule to built it".format(self.requires))
        #    await construct(self.requires)
            # await bot.do(bot.build(self.requires))
            
         
        e = await self.action(bot)
        
        if not e and not self.is_repeatable:
            self.is_done = True
            #print("Increase supply by {0} to cum supply {1}".format(self.increased_supply, bot.cum_supply))
            bot.cum_supply = bot.cum_supply + self.increased_supply
            bot.build_order.worker_count = bot.build_order.worker_count + self.increase_workers
        return e

    def allow_repeat(self):
        self.is_repeatable = True
        self.is_done = False
        return self


def expand(prioritize=False, repeatable=True):
    async def do_expand(bot):
        building = bot.basic_townhall_type
        can_afford = bot.can_afford(building)
        if can_afford:
            return await bot.expand_now(building=building)
        else:
            return can_afford.action_result

    return Command(do_expand, priority=prioritize, repeatable=repeatable, increase_workers = worker_expand_increase)


def train_unit(unit, on_building, prioritize=False, repeatable=False, increased_supply = 0):

   
    async def do_train(bot):
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

    return Command(do_train, priority=prioritize, repeatable=repeatable, increased_supply= increased_supply, requires =  unit_requirements.get(unit))


def morph(unit, prioritize=False, repeatable=False, increased_supply = 0):
    async def do_morph(bot):
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

    return Command(do_morph, priority=prioritize, repeatable=repeatable, increased_supply = increased_supply)


def construct(building, placement=None, prioritize=True, repeatable=False):
    async def do_build(bot):


        if not placement:
            location = bot.townhalls.first.position.towards(bot.game_info.map_center, 5)
        else:
            location = placement

        can_afford = bot.can_afford(building)
        if can_afford:
            print("Building {}".format(building))
            return await bot.build(building, near=location)
        else:
            return can_afford.action_result

    return Command(do_build, priority=prioritize, repeatable=repeatable, requires =  construct_requirements.get(building))


def add_supply(prioritize=True, repeatable=False):
    async def supply_spec(bot):
        can_afford = bot.can_afford(bot.supply_type)
        if can_afford:
            if bot.race == Race.Zerg:
                return await morph(bot.supply_type).execute(bot)
            else:
                return await construct(bot.supply_type).execute(bot)
        else:
            return can_afford.action_result

    return Command(supply_spec, priority=prioritize, repeatable=repeatable)


def add_gas(prioritize=True, repeatable=False):
    async def do_add_gas(bot):
        can_afford = bot.can_afford(bot.geyser_type)
        if not can_afford:
            return can_afford.action_result

        owned_expansions = bot.owned_expansions
        for location, th in owned_expansions.items():
            vgs = bot.state.vespene_geyser.closer_than(20.0, th)
            for vg in vgs:
                worker = bot.select_build_worker(vg.position)
                if worker is None:
                    break

                if not bot.units(bot.geyser_type).closer_than(1.0, vg).exists:
                    return await bot.do(worker.build(bot.geyser_type, vg))

        return ActionResult.Error

    return Command(do_add_gas, priority=prioritize, repeatable=repeatable, increase_workers=worker_gas_increase)





async def build_required(self, bot, required):
    """Builds required building"""

    if command_requires is None:
        return
      
    
    

    #if not unit_count_at_least(command_requires, 1, True):
    #   await build_required(self, bot, construct_requirements[command_requires])
    
    prerequired = construct_requirements[required]


    if required in building_addons:
        pass

    if bot.units.owned(prerequired):
        pass

    




    # deprecated
    # TODO count units properly as in count_unit
    amount_requires = 0
    amount_prerequires = 0

    if False:
        prerequires = prerequired
        if command_requires in building_addons:
            for building in bot.units(command_requires):
                if not building.has_add_on:
                    amount_requires += 1
            for building in bot.units(prerequires):
                if not building.has_add_on:
                    amount_prerequires += 1
        else:
            amount_requires = bot.units(command_requires).amount 
            amount_prerequires = bot.units(prerequires).amount  

        if amount_requires + bot.already_pending(command_requires)  > 0:
            return
        elif amount_prerequires + bot.already_pending(prerequires) == 0:
            await build_required(self, bot, prerequires)
        elif amount_requires == 0 and amount_prerequires >= 1 and bot.can_afford(command_requires): 
            print("Build new building {0} due to requirements".format(command_requires))
            if command_requires in building_addons:
                await train_unit(command_requires, prerequires).execute(bot)
            else:
                await construct(command_requires).execute(bot)