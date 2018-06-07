import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.build_orders.build_order import BuildOrder, train_unit
from sc2.build_orders.commands import construct, expand, add_supply, add_gas, train_unit
from strategy_constants import *
from sc2.player import Bot, Computer
from sc2.state_conditions.conditions import all_of, supply_at_least, minerals_at_least, unit_count

from math import isclose
from random import sample, randrange
from abc import ABCMeta, abstractmethod, abstractproperty

from strategy_util import *

class Bot_AI_Extended(sc2.BotAI):
    """Extends BotAI with specific methods for the strategy"""

    def __init__(self, path):
        build_order = init_build_order(path)
        self.attack = False
        self.defending = False
        self.build_order = BuildOrder(self, build_order, worker_count=init_worker_count)

    async def on_step(self, iteration):
        if iteration >= max_iterations:
            raise TimeoutError

        await self.distribute_workers()
        await self.build_order.execute_build()

        # check every 2 seconds
        if iteration % gameloops_check_frequency*2 == 0: 
            await auto_build(self)

        # check every second
        if iteration % gameloops_check_frequency == 0:
            await auto_attack(self)
            await auto_defend(self)

# TODO check if works  
async def auto_defend(bot):
    if bot.defending or bot.known_enemy_units.amount > 0:
        units_military = get_units_military(bot)
        units_military_amount = len(units_military)
        close_enemies =  bot.known_enemy_units.closer_than(distance_defend, bot.townhalls.random)
        if close_enemies.amount > 0 and units_military_amount >= min_units_attack and bot.known_enemy_units.amount <= units_military_amount*2:          
            print("Enemy detected")
            bot.defending = True 

            for unit in filter(lambda u: u.is_idle, units_military):  
                enemy = close_enemies.random # attack random unit
                if enemy.distance_to(bot.townhalls.random) < distance_defend:
                    await bot.do(unit.attack(enemy.position.to2, queue=True))



async def auto_attack(bot):
    units_military = get_units_military(bot)
    units_military_amount = len(units_military)
    if bot.attack or units_military_amount >= min_units_attack:
                   
        bot.attack = True
               
        for unit in filter(lambda u: u.is_idle, units_military):   
            if bot.known_enemy_structures.exists:
                enemy = bot.known_enemy_structures.first # focus on building
                await bot.do(unit.attack(enemy.position.to2, queue=True))
            if bot.known_enemy_units.exists:
                enemy = bot.known_enemy_units.random # attack random unit
                await bot.do(unit.attack(enemy.position.to2, queue=True))
            await bot.do(unit.attack(bot.enemy_start_locations[0]))
    return           
 



async def auto_build(bot):
            
     # if much --> build new terran_military_buildings
    if bot.minerals > sufficently_much_minerals and bot.vespene > sufficently_much_vespene and bot.units.structure.idle < auto_build_idle_limit:  
        for building in sample(terran_military_buildings, terran_military_buildings_sample):
            building_required = construct_requirements[building]
            if bot.units(building_required).owned.completed.amount > 0:      
                print("Build {0} due to a large surplus of resources".format(building))
                bot.cum_supply = bot.cum_supply + 2 # in case of stopped build order
                await bot.build(building, near = get_random_building_location(bot))
    elif bot.minerals > sufficently_much_minerals and bot.units(bot.basic_townhall_type).pending.amount == 0:
        print("Auto expand due to a large surplus of resources")
        await expand().execute(bot)

    
        

    # sample order for different units
    # build units if enough resources
    if bot.minerals > sufficently_enough_minerals and bot.vespene > sufficently_enough_vespene:  # and bot.can_afford(unit) 
        for unit in sample(terran_military_units_vepene, terran_military_units_vepene_sample): 
            building_required = unit_requirements[unit]

            if building_required in building_addons:
                building_required = construct_requirements[building_required]

            # find at least one idle building that can built the unit
            for building in bot.units(building_required).owned.completed.idle:
                if can_build(building, unit) and bot.can_afford(unit) : # and count_units(bot, building_required, True) > 0:
                        print("Train unit {0} due to surplus of resources".format(unit))
                        bot.cum_supply = bot.cum_supply + 1
                        await bot.do(building.train(unit))

                        #await train_unit(unit, building_required, 1).execute(bot) # increase only by one in order not to miss up the build order


    # build units if enough resources
    if bot.minerals > sufficently_enough_minerals and bot.vespene < sufficently_enough_vespene:  
        for unit in sample(terran_military_units_mineral, terran_military_units_mineral_sample): # shuffle(terran_military_units_mineral):
            building_required = unit_requirements[unit]

            if building_required in building_addons:
                building_required = construct_requirements[building_required]

            # find at least one idle building that can built the unit
            for building in bot.units(building_required).owned.completed.idle:
                if can_build(building, unit)  and bot.can_afford(unit) :
                #if building.noqueue and building.is_idle and count_units(bot, building_required, True) > 0:
                        print("Train unit {0} due to surplus of minerals".format(unit))
                        bot.cum_supply = bot.cum_supply + 1
                        await bot.do(building.train(unit))
                        # await train_unit(unit, building_required, 1).execute(bot) # increase only by one in order not to miss up the build order




