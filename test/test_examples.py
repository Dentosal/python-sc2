import pytest

import sc2
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer

from examples.terran.proxy_rax import ProxyRaxBot
from examples.terran.ramp_wall import RampWallBot
from examples.protoss.cannon_rush import CannonRushBot
from examples.protoss.warpgate_push import WarpGateBot
from examples.zerg.zerg_rush import ZergRushBot
from examples.zerg.onebase_broodlord import BroodlordBot

def run_example(race, bot):
    result = sc2.run_game(sc2.maps.get("Sequencer LE"), [
        Bot(race, bot),
        Computer(Race.Terran, Difficulty.Easy)
    ], realtime=False)

    assert result in [sc2.Result.Victory, sc2.Result.Defeat, sc2.Result.Tie]


@pytest.mark.slow
def test_proxy_rax_example():
    run_example(Race.Terran, ProxyRaxBot())

@pytest.mark.slow
def test_ramp_wall_example():
    run_example(Race.Terran, RampWallBot())

@pytest.mark.slow
def test_cannon_rush_example():
    run_example(Race.Protoss, CannonRushBot())

@pytest.mark.slow
def test_warpgate_example():
    run_example(Race.Protoss, WarpGateBot())

@pytest.mark.slow
def test_zerg_rush_example():
    run_example(Race.Zerg, ZergRushBot())

@pytest.mark.slow
def test_broodlord_example():
    run_example(Race.Zerg, BroodlordBot())
