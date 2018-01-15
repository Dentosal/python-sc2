import pytest

import sc2
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer

from examples.proxy_rax import ProxyRaxBot
from examples.cannon_rush import CannonRushBot
from examples.zerg_rush import ZergRushBot

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
def test_cannon_rush_example():
    run_example(Race.Protoss, CannonRushBot())

@pytest.mark.slow
def test_zerg_rush_example():
    run_example(Race.Zerg, ZergRushBot())
