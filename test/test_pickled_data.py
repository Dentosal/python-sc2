import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
# sys.path.append("/root/template")

from sc2.game_data import GameData
from sc2.game_info import GameInfo
from sc2.game_info import Ramp
from sc2.game_state import GameState
from sc2.bot_ai import BotAI
from sc2.units import Units
from sc2.unit import Unit
from sc2.unit import UnitGameData
from sc2.position import Point2, Point3, Size, Rect

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.effect_id import EffectId

from sc2.data import Race

import pickle, pytest, random, math
from hypothesis import given, event, settings, strategies as st

from typing import Iterable


"""
You can execute this test running the following command from the root python-sc2 folder:
pipenv run pytest test/test_pickled_data.py --hypothesis-show-statistic
"""


def get_map_specific_bots() -> Iterable[BotAI]:
    folder = os.path.dirname(__file__)
    subfolder_name = "pickle_data"
    pickle_folder_path = os.path.join(folder, subfolder_name)
    files = os.listdir(pickle_folder_path)
    for file in (f for f in files if f.endswith(".pkl")):
        with open(os.path.join(folder, subfolder_name, file), "rb") as f:
            raw_game_data, raw_game_info, raw_observation = pickle.load(f)

        # Build fresh bot object, and load the pickle'd data into the bot object
        bot = BotAI()
        game_data = GameData(raw_game_data.data)
        game_info = GameInfo(raw_game_info.game_info)
        game_state = GameState(raw_observation)
        UnitGameData._game_data = game_data
        bot._prepare_start(None, 1, game_info, game_data)
        bot._prepare_step(game_state)

        yield bot


# From https://docs.pytest.org/en/latest/example/parametrize.html#a-quick-port-of-testscenarios
def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    for scenario in metafunc.cls.scenarios:
        idlist.append(scenario[0])
        items = scenario[1].items()
        argnames = [x[0] for x in items]
        argvalues.append(([x[1] for x in items]))
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


# Global bot object that is used in TestClass.test_position_*
random_bot_object = next(get_map_specific_bots())


class TestClass:
    # Load all pickle files and convert them into bot objects from raw data (game_data, game_info, game_state)
    scenarios = [(bot_obj.game_info.map_name, {"bot": bot_obj}) for bot_obj in get_map_specific_bots()]

    def test_bot_ai(self, bot: BotAI):
        # Test initial bot attributes at game start

        # Properties from _prepare_start
        assert 1 <= bot.player_id <= 2
        assert isinstance(bot.race, Race)
        assert isinstance(bot.enemy_race, Race)

        # Properties from _prepare_step
        assert bot.units.amount == bot.townhalls.amount + bot.workers.amount
        assert bot.workers.amount == 12
        assert bot.townhalls.amount == 1
        assert bot.geysers.amount == 0
        assert bot.minerals == 50
        assert bot.vespene == 0
        assert bot.supply_army == 0
        assert bot.supply_workers == 12
        assert bot.supply_cap == 15
        assert bot.supply_used == 12
        assert bot.supply_left == 3
        assert bot.idle_worker_count == 0
        assert bot.army_count == 0

        # Test bot_ai functions
        assert bot.time == 0
        assert bot.time_formatted in {"0:00", "00:00"}
        assert bot.nuke_detected is False
        assert bot.nydus_detected is False
        assert bot.start_location is None  # Is populated by main.py
        bot._game_info.player_start_location = bot.townhalls.random.position
        assert bot.townhalls.random.position not in bot.enemy_start_locations
        assert bot.known_enemy_units == Units([])
        assert bot.known_enemy_structures == Units([])
        bot._game_info.map_ramps = bot._game_info._find_ramps()
        assert bot.main_base_ramp  # Test if any ramp was found
        # TODO: Cache all expansion positions for a map and check if it is the same
        assert len(bot.expansion_locations) >= 12
        # On N player maps, it is expected that there are N*X bases because of symmetry, at least for 1vs1 maps
        assert len(bot.expansion_locations) % (len(bot.enemy_start_locations) + 1) == 0
        # for location in [bot._game_info.player_start_location] + bot.enemy_start_locations:
        #     assert location in set(bot.expansion_locations.keys()), f"{location}, {set(bot.expansion_locations.keys())}"

        # The following functions need to be tested by autotest_bot.py because they use API query which isn't available here as this file only uses the pickle files
        # get_available_abilities
        # expand_now
        # get_next_expansion
        # distribute_workers
        # assert bot.owned_expansions == {bot.townhalls.first.position: bot.townhalls.first}
        assert bot.can_feed(UnitTypeId.MARINE)
        assert bot.can_feed(UnitTypeId.SIEGETANK)
        assert not bot.can_feed(UnitTypeId.THOR)
        assert not bot.can_feed(UnitTypeId.BATTLECRUISER)
        assert bot.can_afford(UnitTypeId.SCV)
        assert bot.can_afford(UnitTypeId.MARINE)
        assert not bot.can_afford(UnitTypeId.SIEGETANK)
        assert not bot.can_afford(UnitTypeId.BATTLECRUISER)
        # can_cast
        worker = bot.workers.random
        assert bot.select_build_worker(worker.position) == worker
        for w in bot.workers:
            if w == worker:
                continue
            assert bot.select_build_worker(w.position) != worker
        # can_place
        # find_placement
        assert bot.already_pending_upgrade(UpgradeId.STIMPACK) == 0
        assert bot.already_pending(UpgradeId.STIMPACK) == 0
        assert bot.already_pending(UnitTypeId.SCV) == 0
        # build
        # do
        # do_actions
        # chat_send
        assert 0 < bot.get_terrain_height(worker)
        assert bot.in_placement_grid(worker)
        assert bot.in_pathing_grid(worker)
        assert bot.is_visible(worker)
        # The pickle data was created by a terran bot
        assert not bot.has_creep(worker)

    def test_game_info(self, bot: BotAI):
        game_info: GameInfo = bot._game_info

        # Test if main base ramp works
        ramp: Ramp = bot.main_base_ramp
        assert ramp.barracks_correct_placement
        assert ramp.barracks_in_middle
        assert ramp.depot_in_middle
        assert len(ramp.corner_depots) == 2
        assert ramp.top_center
        assert ramp.bottom_center
        assert ramp.size
        assert ramp.points
        assert ramp.upper2_for_ramp_wall
        assert ramp.upper
        assert ramp.lower

        # Test game info object
        assert len(game_info.players) == 2
        assert game_info.map_name
        assert game_info.local_map_path
        assert game_info.map_size
        assert game_info.pathing_grid
        assert game_info.terrain_height
        assert game_info.placement_grid
        assert game_info.playable_area
        assert game_info.map_center
        assert game_info.map_ramps
        assert game_info.player_races
        assert game_info.start_locations
        assert game_info.player_start_location

    def test_game_data(self, bot: BotAI):
        game_data = bot._game_data
        assert game_data.abilities
        assert game_data.units
        assert game_data.upgrades
        assert len(game_data.unit_types) == 2  # Filled with CC and SCV from previous tests

    def test_game_state(self, bot: BotAI):
        state = bot.state

        assert not state.actions
        assert not state.action_errors
        assert not state.dead_units
        assert not state.alerts
        assert not state.player_result
        assert not state.chat
        assert state.common
        assert state.psionic_matrix
        assert state.game_loop == 0
        assert state.score
        assert state.own_units == bot.units
        assert not state.enemy_units
        assert state.mineral_field
        assert state.vespene_geyser
        assert state.resources
        # There may be maps without destructables
        assert isinstance(state.destructables, (list, set, dict))
        assert state.units
        assert not state.upgrades
        assert not state.dead_units
        assert not state.blips
        assert state.visibility
        assert state.creep
        assert not state.effects

    def test_pixelmap(self, bot: BotAI):
        pass

    def test_score(self, bot: BotAI):
        pass

    def test_unit(self, bot: BotAI):
        pass

    def test_units(self, bot: BotAI):
        pass

    @given(
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
    )
    @settings(max_examples=500)
    def test_position_pointlike(self, bot: BotAI, x1, y1, x2, y2, x3, y3):
        # event(f"{x1}, {y1}, {x2}, {y2}")
        # asd = {hash(Point2((2, 2))), hash(Point2((-1, -1))), hash(Point2((0, 1))), hash(Point2((-2, -1)))}
        # event(f"{x1} yolo {asd}, {len(asd)}")
        unit1: Unit = random_bot_object.units.random
        unit2: Unit = next(u for u in random_bot_object.units if u.tag != unit1.tag)
        pos1 = Point2((x1, y1))
        pos2 = Point2((x2, y2))
        pos3 = Point2((x3, y3))
        assert pos1.position == pos1
        dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        # event(f"Values were {pos1} and {pos2}, dist is {dist}")
        assert pos1.distance_to(pos2) == dist
        assert pos1.old_distance_to(pos2) == dist
        assert pos1.distance_to_point2(pos2) == dist
        assert pos1._distance_squared(pos2) ** 0.5 == dist

        epsilon = 1e-1
        if epsilon < dist < 1e10:
            assert pos1.is_closer_than(dist + epsilon, pos2)
            assert pos1.is_further_than(dist - epsilon, pos2)

        points = {pos2, pos3}
        points2 = {pos1, pos2, pos3}
        # All 3 points need to be different
        if len(points2) == 3:
            assert pos1.sort_by_distance(points2) == sorted(points2, key=lambda p: pos1._distance_squared(p))
            assert pos1.closest(points2) == pos1
            closest_point = min(points, key=lambda p: p._distance_squared(pos1))
            dist_closest_point = pos1._distance_squared(closest_point) ** 0.5
            furthest_point = max(points, key=lambda p: p._distance_squared(pos1))
            dist_furthest_point = pos1._distance_squared(furthest_point) ** 0.5

            # Distances between pos1-pos2 and pos1-pos3 might be the same, so the sorting might still be different, that's why I use a set here
            assert pos1.closest(points) in {p for p in points2 if pos1.distance_to(p) == dist_closest_point}
            assert pos1.distance_to_closest(points) == pos1._distance_squared(closest_point) ** 0.5
            assert pos1.furthest(points) in {p for p in points2 if pos1.distance_to(p) == dist_furthest_point}
            assert pos1.distance_to_furthest(points) == pos1._distance_squared(furthest_point) ** 0.5
            assert pos1.offset(pos2) == Point2((pos1.x + pos2.x, pos1.y + pos2.y))
            if pos1 != pos2:
                assert pos1.unit_axes_towards(pos2) != Point2((0, 0))

            if 0 < x3:
                temp_pos = pos1.towards(pos2, x3)
                if x3 <= pos1.distance_to(pos2):
                    # Using "towards" function to go between pos1 and pos2
                    dist1 = pos1.distance_to(temp_pos) + pos2.distance_to(temp_pos)
                    dist2 = pos1.distance_to(pos2)
                    assert abs(dist1 - dist2) <= epsilon
                else:
                    # Using "towards" function to go past pos2
                    dist1 = pos1.distance_to(pos2) + pos2.distance_to(temp_pos)
                    dist2 = pos1.distance_to(temp_pos)
                    assert abs(dist1 - dist2) <= epsilon
            elif x3 < 0:
                # Using "towards" function with a negative value
                temp_pos = pos1.towards(pos2, x3)
                dist1 = temp_pos.distance_to(pos1) + pos1.distance_to(pos2)
                dist2 = pos2.distance_to(temp_pos)
                assert abs(dist1 - dist2) <= epsilon

        assert pos1 == pos1
        assert pos2 == pos2
        assert pos3 == pos3
        assert isinstance(hash(pos1), int)
        assert isinstance(hash(pos2), int)
        assert isinstance(hash(pos3), int)

    @given(
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
    )
    @settings(max_examples=500)
    def test_position_point2(self, bot: BotAI, x1, y1, x2, y2):
        pos1 = Point2((x1, y1))
        pos2 = Point2((x2, y2))
        assert pos1.x == x1
        assert pos1.y == y1
        assert pos1.to2 == pos1
        assert pos1.to3 == Point3((x1, y1, 0))
        assert pos1.distance2_to(pos2) == pos1._distance_squared(pos2)
        if 0 < x2:
            assert pos1.random_on_distance(x2) != pos1
            assert pos1.towards_with_random_angle(pos2, x2) != pos1
        assert pos1.towards_with_random_angle(pos2) != pos1
        if pos1 != pos2:
            dist = pos1.distance_to(pos2)
            intersections1 = pos1.circle_intersection(pos2, r=dist / 2)
            assert len(intersections1) == 1
            intersections2 = pos1.circle_intersection(pos2, r=dist * 2 / 3)
            assert len(intersections2) == 2
        neighbors4 = pos1.neighbors4
        assert len(neighbors4) == 4
        neighbors8 = pos1.neighbors8
        assert len(neighbors8) == 8

        assert pos1 + pos2 == Point2((x1 + x2, y1 + y2))
        assert pos1 - pos2 == Point2((x1 - x2, y1 - y2))
        assert pos1 * pos2 == Point2((x1 * x2, y1 * y2))
        if 0 not in {x2, y2}:
            assert pos2
            assert pos1 / pos2 == Point2((x1 / x2, y1 / y2))

        if pos1._distance_squared(pos2) < 0.1:
            assert pos1.is_same_as(pos2, dist=0.1)

        assert pos1.unit_axes_towards(pos2) == pos1.direction_vector(pos2)

    @given(
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
    )
    @settings(max_examples=10)
    def test_position_point2(self, bot: BotAI, x1, y1, z1):
        pos1 = Point3((x1, y1, z1))
        assert pos1.z == z1
        assert pos1.to3 == pos1

    @given(st.integers(min_value=-1e10, max_value=1e10), st.integers(min_value=-1e10, max_value=1e10))
    @settings(max_examples=20)
    def test_position_size(self, bot: BotAI, w, h):
        size = Size((w, h))
        assert size.width == w
        assert size.height == h

    @given(
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
        st.integers(min_value=-1e10, max_value=1e10),
    )
    @settings(max_examples=20)
    def test_position_rect(self, bot: BotAI, x, y, w, h):
        rect = Rect((x, y, w, h))
        assert rect.x == x
        assert rect.y == y
        assert rect.width == w
        assert rect.height == h
        assert rect.size == Size((w, h))
        assert rect.center == Point2((rect.x + rect.width / 2, rect.y + rect.height / 2))
        assert rect.offset((1, 1)) == Rect((x + 1, y + 1, w, h))
