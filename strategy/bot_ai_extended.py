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

    def init_loggers(self):
        """Defines logging levels"""
        logger_strategy = logging.getLogger("sc2.strategy")        
        logger_strategy.setLevel(logging.DEBUG)       
    
        logger_command = logging.getLogger("sc2.command")
        logger_command.setLevel(logging.DEBUG)   


    def get_buildorder(self, path, logger):
        """Gets build-order, can be overwritten e.g. in strategy_test"""
        return init_build_order(path, logger)

    def __init__(self, path = None, output_replay = None, logger = logging.getLogger("sc2.strategy")):
        """Initialised bot"""
        self.init_loggers()

        self.attack = False
        self.defending = False
        self.researched = [] # list of researched
        self.build_order = BuildOrder(self, self.get_buildorder(path, logger), worker_count=init_worker_count)
        self.first_base = None # location of first own base
        self.path = output_replay # output replay path
        self.enemy_base = None # location of first enemy base
        self.logger = logger
        
        global distance_attack
        self.distance_attack_current = distance_attack # current attacking distance to enemy base

        global min_units_attack
        self.min_units_attack = min_units_attack # minimum units required to attack

    
    async def on_step(self, iteration):
        """Execute every iteration"""
        
        if self.first_base is None:
            self.first_base = self.units(UnitTypeId.COMMANDCENTER).first 
                
       
        # check if game lost -> give up
        if iteration % gameloops_check_frequency == 0:
            # if first base is destroyed --> died
            cc = self.units(UnitTypeId.COMMANDCENTER) | self.units(UnitTypeId.ORBITALCOMMAND)
            if self.units.find_by_tag(self.first_base.tag) is None or cc.amount == 0: 
                await self.chat_send("gg")
                self.final_result = result_lost
                export_result(self, result_lost)
                return
            
        if iteration % gameloops_check_frequency / 4 == 0:
            await self.build_order.increase_supply()
            await self.build_order.increase_workers()   
        
        if (iteration + 1) % gameloops_check_frequency == 0:
            await self.distribute_workers()

        if (iteration + 2)  % gameloops_check_frequency / 2 == 0:
            await self.build_order.execute_build()

        if (iteration + 4) % gameloops_check_frequency / 2 == 0:
            await self.auto_build_buildings()

        if (iteration + 6) % gameloops_check_frequency / 2 == 0:
            await self.auto_build_units(UnitTypeId.FACTORY, auto_build_factory_units)

        if (iteration + 8) % gameloops_check_frequency / 2 == 0:
            await self.auto_build_units(UnitTypeId.BARRACKS, auto_build_barracks_units)

        if (iteration + 10) % gameloops_check_frequency / 2 == 0:
            await self.auto_build_units(UnitTypeId.STARPORT, auto_build_starport_units)

        if (iteration + 12) % gameloops_check_frequency / 2 == 0:
            await self.auto_build_expand()
            
        if (iteration + 13) % gameloops_check_frequency == 0:
           await self.auto_defend()  

        if (iteration + 14) % gameloops_check_frequency == 0:
           await self.auto_attack()   
           
        # always build gas on all expansions
        if (iteration + 15) % gameloops_check_frequency * 10 == 0 and self.supply_used > 30:
           await add_gas().execute(self)



    @measure_runtime
    async def auto_defend(self):
        """Defends against enemy"""

        if self.townhalls.amount == 0:
            return

        if self.defending or self.known_enemy_units.amount > 0:
            units_military = self.units.owned.military 
            units_military_amount = len(units_military)
            close_enemies =  self.known_enemy_units.closer_than(distance_defend, self.townhalls.random)
            # if there are close enemies and sufficiently enough units -> defend
            if close_enemies.amount > 0 and (units_military_amount >= min_units_defend or self.known_enemy_units.amount <= units_military_amount):       
            
                if not self.defending:
                    print_log(self.logger, logging.DEBUG, "Defending")
                    self.defending = True 
                    self.attack = False
                    # increase distance to enemy
                    if self.distance_attack_current + 3 * distance_attack_speed <= distance_attack:
                        self.distance_attack_current = self.distance_attack_current + 3 * distance_attack_speed

            
                list_actions = []
                for unit in units_military: 
                        enemy = close_enemies.random # attack random unit
                        if enemy.distance_to(self.townhalls.random) < distance_defend:
                            list_actions.append(unit.attack(enemy.position.to2, queue=True))
                await self.execute_actions(list_actions)

            elif self.defending == True:
                # enemy too far away, or too few units
                print_log(self.logger, logging.DEBUG, "Not defending")
                self.defending = False


    @measure_runtime
    async def execute_actions(self, list_action):
        """Executing actions as list improves the performance significantly"""
        # minerals and gas are not checked, instead use for moving units
        await self._client.actions(list_action, self._game_data)


    @measure_runtime
    async def auto_attack(self):
        """Automatic attack opponent; Priority: Attack units first, then buildings, else enemy base"""

        # do not attack and defend at same time
        if self.defending == True:
            return
   
        units_military = self.units.owned.military 
        units_military_amount = len(units_military)
        enemy_position = None # i.e. either unit, building or opponents base

        if units_military_amount <= retreating_level * min_units_attack and self.attack == True:
            # Retreat
            print_log(self.logger, logging.DEBUG, "Not attacking")
            self.attack = False

            # reset to distance attack
            global distance_attack
            self.distance_attack_current = distance_attack

            # army too week, try next time with more units
            if self.min_units_attack < always_units_attack:
                self.min_units_attack = self.min_units_attack + min_units_attack_increment
        
        elif self.attack or units_military_amount >= self.min_units_attack:
            if self.attack == False:
                print_log(self.logger, logging.DEBUG, "Attacking")           
                self.attack = True
                self.defending = False
          
            # Attack units    
            if self.known_enemy_units.exists:
                enemy = self.known_enemy_units.random # attack random unit
                enemy_position = enemy.position.to2

            # Attack buildings
            enemy_buildings = self.known_enemy_structures
            if enemy_buildings.exists:
                if enemy_position is None:
                    enemy_position = enemy_buildings.first.position.to2 # focus on single building

                # determine enemy base
                if self.enemy_base is None:
                    enemy_bases = enemy_buildings.townhall

                    for base in enemy_bases:
                        distance = base.position.to2.distance_to(self.enemy_start_locations[0])
                        if distance < 1:
                            self.enemy_base = base
   

            # Attack base if neither unit nor building is known
            if enemy_position is None: 
                # approach enemy base by distance_attack_speed steps
                if self.distance_attack_current > 0:
                    self.distance_attack_current = self.distance_attack_current - distance_attack_speed
                        
                enemy_position = self.enemy_start_locations[0].towards(self.first_base.position, self.distance_attack_current)

            # Check if enemy base is destroyed        
            if self.enemy_base is not None: 
                won_destroyed = True
                # tags might change over time, thus comparison wont work on tags
                # therefore compare by distance
                for building in enemy_buildings.townhall:
                    # if there is a base -> not destroyed                
                    if building.position.to2.distance_to(self.enemy_start_locations[0]) < 1:
                        won_destroyed = False

                if won_destroyed == True: 
                    self.final_result = result_won
                    export_result(self, result_won)
                    return
         
        
            list_actions = []
            for unit in units_military: 
                list_actions.append(unit.attack(enemy_position, queue=False))
            await self.execute_actions(list_actions)
                
        return           
 
    @measure_runtime
    async def auto_build_expand(self):
        """Auto build expansion in case of surplus of resources"""

        if self.minerals > sufficently_gigantic_minerals and self.units(self.basic_townhall_type).pending.amount == 0 :
            print_log(self.logger, logging.DEBUG, "Auto expand due to a gigantic surplus of resources")
            await expand().execute(self)      
        

    @measure_runtime
    async def auto_build_buildings(self):            
        """Auto build terran_military_buildings in case of large surplus of resources"""

        if self.minerals > sufficently_much_minerals or self.vespene > sufficently_much_vespene:  
            # build random terran building
            building = sample(terran_military_buildings, 1)[0] # select one random building
            building_required = construct_requirements[building]
            # if requirements fulfilled
            if self.units(building_required).owned.completed.amount > 0 and self.can_afford(building):      
                print_log(self.logger, logging.DEBUG, "Build {0} due to a large surplus of resources".format(building))
                self.cum_supply = self.cum_supply + supply_increase_autobuild_buildings # in case of bringing the gap in build-order
                await self.build(building, near = get_random_building_location(self))

    @measure_runtime
    async def auto_build_units(self, building_id, units_list):
        """Auto build units in case of surplus of resources"""

        if self.minerals > sufficently_enough_minerals or self.vespene > sufficently_enough_vespene:  
            # for idle buildings, build random unit             
            for building in self.units(building_id).owned.completed.idle: 

                unit = sample(units_list, 1)[0] # random unit

                if can_build(building, unit) and self.can_afford(unit):
                    print_log(self.logger, logging.DEBUG, "Train unit {0} due to surplus of resources".format(unit))
                    #self.cum_supply = self.cum_supply + 0.5
                    await self.do(building.train(unit))