import sc2
from sc2 import run_game, maps, Race, Difficulty, sc_pb
from sc2.build_orders.build_order import BuildOrder, train_unit
from sc2.build_orders.commands import construct, expand, add_supply, add_gas, train_unit
from strategy_constants import *
from sc2.player import Bot, Computer
from sc2.state_conditions.conditions import all_of, supply_at_least, minerals_at_least, unit_count, unit_count_at_least_completed
from math import isclose
from random import sample, randrange
from abc import ABCMeta, abstractmethod, abstractproperty
from sc2.data import Result
from strategy_util import *
from util import *
import time
import logging

class Bot_AI_Extended(sc2.BotAI):
    """Extends BotAI with specific methods for the strategy"""




    def __init__(self, path, output_replay, logger):
        init_loggers()

        build_order = init_build_order(path, logger)
        self.attack = False
        self.defending = False
        self.researched = []
        self.build_order = BuildOrder(self, build_order, worker_count=init_worker_count)
        self.first_base = None
        self.path = output_replay
        self.enemy_base = None
        self.logger = logger

        global min_units_attack
        self.min_units_attack = min_units_attack

    



    async def on_step(self, iteration):

        if self.first_base is None:
            self.first_base = self.units(UnitTypeId.COMMANDCENTER).first 
                
       
        # check if game lost -> give up
        if iteration % gameloops_check_frequency == 0:
            # if first base is destroyed --> died
            cc = self.units(UnitTypeId.COMMANDCENTER) | self.units(UnitTypeId.ORBITALCOMMAND)
            if self.units.find_by_tag(self.first_base.tag) is None or cc.amount == 0: # or (cc.amount == 1 and cc.first.health < 1000): # TODO check health
                await self.chat_send("gg")
                self.final_result = result_lost
                export_result(self, result_lost)
                return
            
        if iteration % gameloops_check_frequency / 4 == 0:
            await self.distribute_workers()
            await self.build_order.increase_supply()
            await self.build_order.increase_workers()            

        if (iteration + 2)  % gameloops_check_frequency / 2 == 0:
            await self.build_order.execute_build()

        if (iteration + 4) % gameloops_check_frequency / 2 == 0:
            await auto_build_buildings(self)

        if (iteration + 6) % gameloops_check_frequency / 2 == 0:
            await auto_build_units(self, UnitTypeId.FACTORY, auto_build_factory_units)

        if (iteration + 8) % gameloops_check_frequency / 2 == 0:
            await auto_build_units(self, UnitTypeId.BARRACKS, auto_build_barracks_units)

        if (iteration + 10) % gameloops_check_frequency / 2 == 0:
            await auto_build_units(self, UnitTypeId.STARPORT, auto_build_starport_units)

        if (iteration + 12) % gameloops_check_frequency / 2 == 0:
            await auto_build_expand(self)
            
        if (iteration + 13) % gameloops_check_frequency == 0:
           await auto_defend(self)  
        if (iteration + 14) % gameloops_check_frequency == 0:
           await auto_attack(self)          



@measure_runtime
async def auto_defend(bot):
    """Defends against enemy"""

    if bot.townhalls.amount == 0:
        return

    if bot.defending or bot.known_enemy_units.amount > 0:
        units_military = bot.units.owned.military #get_units_military(bot)
        units_military_amount = len(units_military)
        close_enemies =  bot.known_enemy_units.closer_than(distance_defend, bot.townhalls.random)
        if close_enemies.amount > 0 and (units_military_amount >= min_units_defend or bot.known_enemy_units.amount <= units_military_amount):       
            
            if not bot.defending:
                print_log(bot.logger, logging.DEBUG, "Defending")
                bot.defending = True 


            list_actions = []
            for unit in units_military: #filter(lambda u: u.is_idle, units_military):  
                    enemy = close_enemies.random # attack random unit
                    if enemy.distance_to(bot.townhalls.random) < distance_defend:
                        list_actions.append(unit.attack(enemy.position.to2, queue=True))
            await execute_actions(bot, list_actions)

            #for unit in filter(lambda u: u.is_idle, units_military):  
            #    enemy = close_enemies.random # attack random unit
            #    if enemy.distance_to(bot.townhalls.random) < distance_defend:
            #        await bot.do(unit.attack(enemy.position.to2, queue=True))
        elif bot.defending == True:
            # enemy too far away, or too few units
            print_log(bot.logger, logging.DEBUG, "Not defending")
            bot.defending = False


@measure_runtime
async def execute_actions(bot, list_action):
    """Executing actions as list improves the performance significantly"""
    # minerals and gas are not checked, instead use for moving units
    await bot._client.actions(list_action, bot._game_data)


@measure_runtime
async def auto_attack(bot):
    """Automatic attack opponent; Priority: Attack units first, then buildings, else enemy base"""

    if bot.defending == True:
        return
   
    units_military = bot.units.owned.military 
    units_military_amount = len(units_military)
    enemy_position = None

    if units_military_amount <= min_units_defend and bot.attack == True:
        # Retreat
        print_log(bot.logger, logging.DEBUG, "Not attacking")
        bot.attack = False

        # army too week, try next time with more units
        if bot.min_units_attack < always_units_attack:
            bot.min_units_attack = bot.min_units_attack + min_units_defend
        
    elif bot.attack or units_military_amount >= bot.min_units_attack:
        if bot.attack == False:
            print_log(bot.logger, logging.DEBUG, "Attacking")           
            bot.attack = True
          
        # Attack units    
        if bot.known_enemy_units.exists:
            enemy = bot.known_enemy_units.random # attack random unit
            enemy_position = enemy.position.to2

        # Attack buildings
        enemy_buildings = bot.known_enemy_structures
        if enemy_buildings.exists:
            if enemy_position is None:
                enemy_position = enemy_buildings.first.position.to2 # focus on single building

            if bot.enemy_base is None:
                enemy_bases = enemy_buildings.townhall

                for base in enemy_bases:
                    distance = base.position.to2.distance_to(bot.enemy_start_locations[0])
                    if distance < 1:
                        bot.enemy_base = base
   
        if enemy_position is None: 
                enemy_position = bot.enemy_start_locations[0]

        # Check if enemy base is destroyed
        # diffenet tags wont work
        if bot.enemy_base is not None: #and enemy_buildings.find_by_tag(bot.enemy_base.tag) is None:
            won_destroyed = True
            for building in enemy_buildings.townhall:
                # if there is a base -> not destroyed
                if building.position.to2.distance_to(bot.enemy_start_locations[0]) < 1:
                    won_destroyed = False

            #won_reached = False
            #for unit in units_military:   
            #    if unit.position.to2.distance_to(bot.enemy_start_locations[0]) < 1:
            #        won_reached = True

            if won_destroyed == True: # or won_reached == True:
                bot.final_result = result_won
                export_result(bot, result_won)
                return
         
        
        list_actions = []
        for unit in units_military: # filter(lambda u: u.is_ready, units_military):  
                #await bot.do(unit.attack(enemy_position, queue=False))
                list_actions.append(unit.attack(enemy_position, queue=False))
        await execute_actions(bot, list_actions)
                
    return           
 
@measure_runtime
async def auto_build_expand(bot):
    """Auto build expansion in case of surplus of resources"""

    if bot.minerals > sufficently_gigantic_minerals and bot.units(bot.basic_townhall_type).pending.amount == 0 :
        print_log(bot.logger, logging.DEBUG, "Auto expand due to a gigantic surplus of resources")
        await expand().execute(bot)

@measure_runtime
async def auto_build_buildings(bot):            
    """Auto build terran_military_buildings in case of large surplus of resources"""

    if bot.minerals > sufficently_much_minerals or bot.vespene > sufficently_much_vespene:  
        building = sample(terran_military_buildings, 1)[0] # select one random building
        building_required = construct_requirements[building]

        if bot.units(building_required).owned.completed.amount > 0 and bot.can_afford(building):      
            print_log(bot.logger, logging.DEBUG, "Build {0} due to a large surplus of resources".format(building))
            bot.cum_supply = bot.cum_supply + 1 # in case of bringing the gap in build-order
            await bot.build(building, near = get_random_building_location(bot))

@measure_runtime
async def auto_build_units(bot, building_id, units_list):
    """Auto build units in case of surplus of resources"""

    if bot.minerals > sufficently_enough_minerals or bot.vespene > sufficently_enough_vespene:  
        for building in bot.units(building_id).owned.completed.idle: 
            unit = sample(units_list, 1)[0] # random unit

            if can_build(building, unit) and bot.can_afford(unit):
                print_log(bot.logger, logging.DEBUG, "Train unit {0} due to surplus of resources".format(unit))
                #bot.cum_supply = bot.cum_supply + 0.5
                await bot.do(building.train(unit))