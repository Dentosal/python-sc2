import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.build_orders.build_order import BuildOrder, train_unit
from sc2.build_orders.commands import construct, expand, add_supply, add_gas
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

    
# TODO
def get_units_military(self):
    units_military = []

    for unit in terran_military_units:
        units_military = units_military + self.units(unit)
            
    return  units_military



