from sc2 import ActionResult, Race
from sc2.constants import *
from sc2.state_conditions.conditions import  unit_count_at_least
from random import uniform, randrange
from util import get_random_building_location, print_log
import logging
from strategy_constants import *

class Command(object):

  

    def __init__(self, action, repeatable=False, priority=False, increase_workers = 0, increased_supply = 0, requires = None, requires_2nd = None, max_supply = 200, checkTrainAddon = None):
        self.action = action
        self.is_done = False
        self.is_repeatable = repeatable
        self.is_priority = priority
        self.increase_workers = increase_workers # value to increase workers after executing command
        self.increased_supply = increased_supply # value to increase cum supply after executing command
        self.requires = requires # structure required 
        self.requires_2nd = requires_2nd # 2nd structure required
        self.max_supply = max_supply # otherwise, bot will try to build units over max supply cap yielding ActionResult.FoodUsageImpossible
        self.checkTrainAddon = checkTrainAddon # indicates whether action is training an addon


    # HS modified
    async def execute(self, bot):

        # do not train units if close to supply cap 
        if bot.supply_used > self.max_supply:
            return None
        
        # if requirement not fulfilled, return later
        if self.requires is not None and bot.units(self.requires).completed.amount < 1:
            return None
        if self.requires_2nd is not None and bot.units(self.requires_2nd).completed.amount < 1:
            return None
           
        e = await self.action(bot)
        
        if not e and not self.is_repeatable:
            self.is_done = True            
            bot.cum_supply = bot.cum_supply + self.increased_supply
            bot.build_order.worker_count = bot.build_order.worker_count + self.increase_workers

            #if self.increase_workers > 0:
            #    print("INCREASE WORKERS BY {0} TO {1}".format(self.increase_workers, bot.build_order.worker_count))

        


        return e

    def allow_repeat(self):
        self.is_repeatable = True
        self.is_done = False
        return self


# HS
def checkAddon(unit):
    """Checks whether units is an addon"""
    
    if unit in building_addons:
        return unit
    else:
        return None  

def expand(prioritize=True, repeatable=False):

    async def do_expand(bot):
        building = bot.basic_townhall_type
        can_afford = bot.can_afford(building)
        if can_afford:
            print_log(logging.getLogger("sc2.command"), logging.DEBUG, "Expanding {}".format(building))
            return await bot.expand_now(building=building)
        else:
            return can_afford.action_result

    return Command(do_expand, priority=prioritize, repeatable=repeatable, increase_workers = worker_expand_increase)


# HS modified
def train_unit(unit, on_building, prioritize=False, repeatable=False, increased_supply = 0):
       
    async def do_train(bot):
        buildings = bot.units(on_building).ready.noqueue

        if checkAddon(unit) is not None:
            buildings = buildings.no_add_on

        if buildings.exists:
            selected = buildings.first
            can_afford = bot.can_afford(unit)
            if can_afford:
                print_log(logging.getLogger("sc2.command"), logging.DEBUG, "Training {}".format(unit))
                return await bot.do(selected.train(unit))
            else:
                return can_afford.action_result
 
        else:
            return ActionResult.Error

    return Command(do_train, priority=prioritize, repeatable=repeatable, increased_supply= increased_supply, 
                   requires =  unit_requirements.get(unit), requires_2nd = unit_requirements_2nd.get(unit), 
                   max_supply = 195, checkTrainAddon = checkAddon(unit))


def morph(unit, prioritize=False, repeatable=False, increased_supply = 0):

    async def do_morph(bot):
        larvae = bot.units(UnitTypeId.LARVA)
        if larvae.exists:
            selected = larvae.first
            can_afford = bot.can_afford(unit)
            if can_afford:
                print_log(logging.getLogger("sc2.command"), logging.DEBUG, "Morph {}".format(unit))
                return await bot.do(selected.train(unit))
            else:
                return can_afford.action_result
        else:
            return ActionResult.Error

    return Command(do_morph, priority=prioritize, repeatable=repeatable, increased_supply = increased_supply)

# HS modified
def construct(building, placement=None, prioritize=True, repeatable=False):

    async def do_build(bot):
        
        if not placement:            
            location = get_random_building_location(bot)           
        else:
            location = placement

        can_afford = bot.can_afford(building)
        if can_afford:
            print_log(logging.getLogger("sc2.command"), logging.DEBUG, "Building {}".format(building))
            return await bot.build(building, near=location)
        else:
            return can_afford.action_result

    return Command(do_build, priority=prioritize, repeatable=repeatable, requires = construct_requirements.get(building))


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

# HS modified
def add_gas(prioritize=True, repeatable=False):

    async def do_add_gas(bot):
        can_afford = bot.can_afford(bot.geyser_type)
        if not can_afford:
            return can_afford.action_result

        owned_expansions = bot.owned_expansions
        for location, th in owned_expansions.items():
            # ERROR
            #    File "python-sc2\sc2\build_orders\commands.py", line 184, in do_add_gas
            #    vgs = bot.state.vespene_geyser.closer_than(15.0, th)
            #    File "python-sc2\sc2\game_state.py", line 33, in vespene_geyser
            #    return self.units.vespene_geyser
            #    File "python-sc2\sc2\units.py", line 179, in vespene_geyser
            #    return self.filter(lambda unit: unit.is_vespene_geyser)
            #    File "python-sc2\sc2\units.py", line 110, in filter
            #    return self.subgroup(filter(pred, self))
            #    File "python-sc2\sc2\units.py", line 107, in subgroup
            #    return Units(list(units), self.game_data)
            #    File "python-sc2\sc2\units.py", line 179, in <lambda>
            #    return self.filter(lambda unit: unit.is_vespene_geyser)
            #    File "python-sc2\sc2\unit.py", line 128, in is_vespene_geyser
            #    return self._type_data.has_vespene
            #    File "python-sc2\sc2\unit.py", line 36, in _type_data
            #    return self._game_data.units[self._proto.unit_type]

            vgs = bot.state.vespene_geyser.closer_than(15.0, th)

            if vgs(bot.geyser_type).amount >= 0.5 * vgs.amount:
                # all places already have a geyser building
                continue


            for vg in vgs:
                worker = bot.select_build_worker(vg.position)
                if worker is None:
                    break

                if not bot.units(bot.geyser_type).closer_than(1.0, vg).exists:
                    print_log(logging.getLogger("sc2.command"), logging.DEBUG, "Add Gas")
                    return await bot.do(worker.build(bot.geyser_type, vg))

        return ActionResult.Error

    return Command(do_add_gas, priority=prioritize, repeatable=repeatable, increase_workers=worker_gas_increase)


# HS
def research(upgrade, on_building, prioritize=True):
    """Research upgrade"""

    async def research_spec(bot):
        buildings = bot.units(on_building).completed.noqueue.idle
        if buildings.exists and not upgrade in bot.researched: # already pending wont work with upgrades
       
            can_afford = bot.can_afford(upgrade)
            if can_afford:
                print_log(logging.getLogger("sc2.command"), logging.DEBUG, "Research {0}".format(upgrade))
                bot.researched.append(upgrade)
                await bot.do(buildings.first(upgrade))
            else:
                return can_afford.action_result 
        else:
            return ActionResult.Error

    return Command(research_spec, priority=prioritize, repeatable=False, requires=on_building, requires_2nd = research_requirements.get(upgrade))

# HS
async def build_required(self, bot, required):
    """Builds required building"""

    if required is None or bot.units(required).owned.amount > 0 or not bot.can_afford(required):
        # If no required building or its available (soon) or cannot afford
        return
  
    # Whether the requirement itself has a dependency   
    prerequired = construct_requirements[required]
   

    if prerequired is None or bot.units(prerequired).owned.completed.amount > 0:
        # If prequired fullfilled, just build required

         if required in building_addons:
            if bot.units(prerequired).owned.completed.no_add_on.amount > 0:
                print_log(logging.getLogger("sc2.command"), logging.DEBUG, "Build new addon {0} due to requirements".format(required))
                await train_unit(required, prerequired).execute(bot)
            elif bot.units(prerequired).owned.pending.amount > 0:
                # wait since their are building
                return
            elif bot.can_afford(prerequired):
                # rebuild building, since no empty add_on place
                await build_required(self, bot, prerequired)
         elif bot.already_pending(required) == 0 or bot.units(required).owned.pending.amount == 0:
             print_log(logging.getLogger("sc2.command"), logging.DEBUG, "Build new building {0} due to requirements".format(required))
             await construct(required).execute(bot)
    elif bot.already_pending(prerequired) > 0 or bot.units(prerequired).owned.pending.amount > 0:  
        return
    else:
        # trigger prerequired
        await build_required(self, bot, prerequired)
  