import unittest
from unittest.mock import Mock

from s2clientprotocol import raw_pb2 as raw_pb
from sc2.game_data import GameData
from sc2.unit import Unit
from sc2.position import Point2, Point3
from sc2.ids.unit_typeid import UnitTypeId
from sc2.data import Alliance

class TestUnit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_unit_Marine(self):
        proto_data = Mock(
            spec=raw_pb.Unit,
            unit_type=UnitTypeId.MARINE,
            alliance=Alliance.Self.value,
            tag=245346374,
            pos=Mock(x=-5, y=6, z=50),
            health=35,
            health_max=45,
            energy=0,
            energy_max=0
        )
        game_data = Mock(
            spec=GameData,
            units={UnitTypeId.MARINE: "data"}, # TODO
        )
        marine = Unit(proto_data, game_data)

        self.assertEqual(marine.type_id, UnitTypeId.MARINE)
        self.assertEqual(marine._type_data, "data")
        self.assertEqual(marine.alliance, Alliance.Self.value)
        self.assertTrue(marine.is_mine)
        self.assertEqual(marine.tag, 245346374)
        self.assertEqual(marine.position, Point2((-5, 6)))
        self.assertEqual(marine.position3d, Point3((-5, 6, 50)))
        self.assertEqual(marine.health, 35)
        self.assertEqual(marine.health_max, 45)
        self.assertEqual(marine.health_percentage, 35/45)
        self.assertEqual(marine.energy, 0)
        self.assertEqual(marine.energy_max, 0)
        self.assertEqual(marine.energy_percentage, 0)

if __name__ == "__main__":
    unittest.main()