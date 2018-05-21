import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.build_orders.build_order import BuildOrder, train_unit
from sc2.build_orders.commands import construct, expand, add_supply, add_gas, train_unit
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.state_conditions.conditions import all_of, supply_at_least, minerals_at_least, unit_count

from random import sample, randrange
from abc import ABCMeta, abstractmethod, abstractproperty

from strategy_util import *

class Bot_AI_Extended(sc2.BotAI):
    """Extends BotAI with specific methods for the strategy"""

    def __init__(self, path):
        build_order = init_build_order(path)
        self.attack = False
        self.build_order = BuildOrder(self, build_order, worker_count=init_worker_count)

    
async def auto_attack(bot):
    if bot.attack or len(get_units_military(bot)) >= min_units_attack:
        bot.attack = True
        units_military = get_units_military(bot)
        for unit in filter(lambda u: u.is_idle, units_military):
            await bot.do(unit.attack(bot.enemy_start_locations[0]))
            if bot.known_enemy_structures.exists:
                enemy = bot.known_enemy_structures.first
                await bot.do(unit.attack(enemy.position.to2, queue=True))
    return           
 



async def auto_build(bot):
    
     # if much --> build new terran_military_buildings
    if bot.minerals > sufficently_much_minerals and bot.vespene > sufficently_much_vespene:  
        for building in sample(terran_military_buildings, terran_military_buildings_sample):
            print("Build {0} due to a large surplus of resources".format(building))
            bot.cum_supply = bot.cum_supply + 2 # in case of stopped build order
            await bot.build(building, near = get_random_building_location(bot))
        

    # TODO shuffle or random order for different units
    # build units if enough resources, check every second
    if bot.minerals > sufficently_enough_minerals and bot.vespene > sufficently_enough_vespene:  
        for unit in sample(terran_military_units_vepene, terran_military_units_vepene_sample): # len(terran_military_units_vepene) = 13
            building_required = unit_requirements[unit]
            # find at least one idle building that can built the unit
            for building in bot.units(building_required):
                if building.noqueue and building.is_idle:
                        print("Train unit {0} due to surplus of resources".format(unit))
                        bot.cum_supply = bot.cum_supply + 1
                        await bot.do(building.train(unit))

                        #await train_unit(unit, building_required, 1).execute(bot) # increase only by one in order not to miss up the build order


    # build units if enough resources, check every second
    if bot.minerals > sufficently_enough_minerals and bot.vespene < sufficently_enough_vespene:  
        for unit in sample(terran_military_units_mineral, terran_military_units_mineral_sample): # shuffle(terran_military_units_mineral):
            building_required = unit_requirements[unit]
            # find at least one idle building that can built the unit
            for building in bot.units(building_required):
                if building.noqueue and building.is_idle:
                        print("Train unit {0} due to surplus of minerals".format(unit))
                        bot.cum_supply = bot.cum_supply + 1
                        await bot.do(building.train(unit))
                        # await train_unit(unit, building_required, 1).execute(bot) # increase only by one in order not to miss up the build order




