import unittest

from sc2.position import Point2, Point3, Pointlike

class TestPosition(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.p = Pointlike((2.3, 2.7))
        self.p2 = Point2((-5.3, -7.9))
        self.p3 = Point3((-2.7, 5.4, 133.2))

    def tearDown(self):
        pass

    def test_Pointlike(self):
        self.assertEqual(self.p, Pointlike((2.3, 2.7)))
        self.assertEqual(self.p.rounded, Pointlike((2, 3)))
        self.assertEqual(self.p.position, self.p)
        self.assertEqual(self.p.distance_to(Pointlike((-0.7, 6.7))), 5)
        self.assertEqual(self.p.closest([
            Pointlike((2, 2)),
            Pointlike((-2, -2))
        ]), Pointlike((2, 2)))
        self.assertEqual(self.p.furthest([
            Pointlike((2, 2)),
            Pointlike((-2, -2))
        ]), Pointlike((-2, -2)))
        self.assertEqual(self.p.offset(Pointlike((-1, -1))), Pointlike((1.3, 1.7)))
        self.assertEqual(self.p.offset(Pointlike((-1, 1))), Pointlike((1.3, 3.7)))
        self.assertEqual(self.p.towards(Pointlike((2.3, 50)), 5), Pointlike((2.3, 7.7)))
        # testing backwards aswell
        self.assertEqual(self.p.towards(Pointlike((2.3, 50)), -5), Pointlike((2.3, -2.3)))

    def test_Point2(self):
        self.assertEqual(self.p2.x, -5.3)
        self.assertEqual(self.p2.y, -7.9)
        self.assertEqual(self.p2.to2, self.p2)
        self.assertEqual(self.p2.to3, Point3((-5.3, -7.9, 0)))
        self.assertEqual(self.p2.neighbors4,
            {
                Point2((-5.3, -6.9)),
                Point2((-5.3, -8.9)),
                Point2((-4.3, -7.9)),
                Point2((-6.3, -7.9)),
            })
        self.assertEqual(self.p2.neighbors8, self.p2.neighbors4 |
            {
                Point2((-4.3, -6.9)),
                Point2((-4.3, -8.9)),
                Point2((-6.3, -6.9)),
                Point2((-6.3, -8.9)),
            })

    def test_Point3(self):
        self.assertEqual(self.p3.z, 133.2)
        self.assertEqual(self.p3.to3, self.p3)

    # test Size and Rect missing

if __name__ == "__main__":
    unittest.main()