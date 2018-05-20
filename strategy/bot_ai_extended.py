import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.build_orders.build_order import BuildOrder, train_unit
from sc2.build_orders.commands import construct, expand, add_supply, add_gas, train_unit
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.state_conditions.conditions import all_of, supply_at_least, minerals_at_least, unit_count

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
        
                




