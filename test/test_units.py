import unittest
from unittest.mock import Mock, patch

from s2clientprotocol import raw_pb2 as raw_pb
from sc2.game_data import GameData
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.data import Alliance


class MockGameState(Mock):
    def __init__(self):
        super().__init__(spec=GameData)
        self.units = {UnitTypeId.MARINE: Mock(name="Marine")}
        self.abilities={
                AbilityId.ATTACK: "some data",
                AbilityId.MOVE: "some more data",
            }

class MockProtoData(Mock):
    def __init__(self, **kwargs):
        super().__init__(spec=raw_pb.Unit)
        self.name = "Marine"
        self.unit_type = UnitTypeId.MARINE
        self.alliance = Alliance.Self.value
        self.health = 0
        self.health_max = 0
        self.energy = 0
        self.energy_max = 0
        self.orders = []
        self.__dict__.update(kwargs)

class TestUnits(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     pass

    # @classmethod
    # def tearDownClass(cls):
    #     pass

    def setUp(self):
        mock_proto_data1 = MockProtoData(
            tag=245346374,
            pos=Mock(x=-5, y=6, z=50),
            health=35,
            health_max=45,
            orders=[Mock(ability_id=AbilityId.ATTACK, target_unit_tag=1337, progress=1.0)]
        )
        mock_proto_data2 = MockProtoData(
            tag=245346375,
            pos=Mock(x=-2, y=7, z=50),
            orders=[Mock(ability_id=AbilityId.MOVE, target_world_space_pos=Point2((0, 0)), progress=1.0)]
        )
        mock_proto_data3 = MockProtoData(
            tag=245346376,
            pos=Mock(x=7, y=7, z=50),
        )
        self.mock_game_state = MockGameState()
        self.marine1 = Unit(mock_proto_data1, self.mock_game_state)
        self.marine2 = Unit(mock_proto_data2, self.mock_game_state)
        self.marine3 = Unit(mock_proto_data3, self.mock_game_state)
        self.marines = Units([self.marine1, self.marine2, self.marine3], self.mock_game_state)
        self.emptyUnitsGroup = Units([], self.mock_game_state)

    def tearDown(self):
        # unnecessary here
        del self.marine1
        del self.marine2
        del self.marine3
        del self.marines
        del self.mock_game_state

    def test_amount(self):
        self.assertEqual(self.marines.amount, 3)
        self.assertEqual(self.emptyUnitsGroup.amount, 0)

    def test_empty(self):
        self.assertFalse(self.marines.empty)
        self.assertTrue(self.emptyUnitsGroup.empty)

    def test_exists(self):
        self.assertTrue(self.marines.exists)
        self.assertFalse(self.emptyUnitsGroup.exists)

    def test_find_by_tag(self):
        self.assertEqual(self.marines.find_by_tag(245346374), self.marine1)
        self.assertIsNone(self.marines.find_by_tag(245346))

    def test_first(self):
        self.assertEqual(self.marines.first, self.marine1)

    def test_random(self):
        self.assertTrue(self.marines.random in [self.marine1, self.marine2, self.marine3])

    def test_closest_distance_to(self):
        self.assertEqual(self.marines.closest_distance_to(Point2((10, 10))), (3 ** 2 + 3 ** 2) ** 0.5)

    def test_closest_to(self):
        self.assertEqual(self.marines.closest_to(Point2((10, 10))), self.marine3)

    def test_furthest_to(self):
        self.assertEqual(self.marines.furthest_to(Point2((10, 10))), self.marine1)

    def test_closer_than(self):
        self.assertEqual(self.marines.closer_than(20, Point2((10, 10))), self.marines)
        self.assertEqual(self.marines.closer_than(6, Point2((10, 10))), Units([self.marine3], self.mock_game_state))
        self.assertEqual(self.marines.closer_than(2, Point2((10, 10))), self.emptyUnitsGroup)

    def test_tags_in(self):
        self.assertEqual(self.marines.tags_in({245346374, 245346375}), Units([self.marine1, self.marine2], self.mock_game_state))
        self.assertEqual(self.marines.tags_in({}), self.emptyUnitsGroup)

    def test_tags_not_in(self):
        self.assertEqual(self.marines.tags_not_in({}), self.marines)
        self.assertEqual(self.marines.tags_not_in({245346374}), Units([self.marine2, self.marine3], self.mock_game_state))

    def test_of_type(self):
        self.assertEqual(self.marines.of_type(UnitTypeId.MARINE), self.marines)
        self.assertEqual(self.marines.of_type([UnitTypeId.MARINE]), self.marines)

    def test_exclude_type(self):
        self.assertEqual(self.marines.exclude_type([UnitTypeId.MARINE]), self.emptyUnitsGroup)

    def test_tags(self):
        self.assertSetEqual(self.marines.tags, {u.tag for u in self.marines})

    def test_noqueue(self):
        self.assertEqual(self.marines.noqueue, Units([self.marine3], self.mock_game_state))

    def test_idle(self):
        self.assertEqual(self.marines.idle, Units([self.marine3], self.mock_game_state))

    def test_owned(self):
        self.assertEqual(self.marines.owned, self.marines)

    def test_enemy(self):
        self.assertEqual(self.marines.enemy, self.emptyUnitsGroup)

    def test_contains(self):
        self.assertTrue(UnitTypeId.MARINE in self.marines)

    def test_not_contains(self):
        self.assertFalse(UnitTypeId.ADEPT in self.marines)

if __name__ == "__main__":
    unittest.main()