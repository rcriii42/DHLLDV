import unittest

from DHLLDV.LagrPipe import add_slurries
from DHLLDV.SlurryObj import Slurry


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.slurry1 = Slurry(Cv=0.2)
        self.slurry2 = Slurry(Cv=0.1)

    def test_add_slurries_first_none(self):
        new_slurry = add_slurries((None, 1), (self.slurry2, 1))
        self.assertEqual(new_slurry.rhom, self.slurry2.rhom)

    def test_add_slurries_second_none(self):
        new_slurry = add_slurries((self.slurry1, 1), (None, 1))
        self.assertEqual(new_slurry.rhom, self.slurry1.rhom)

    def test_add_slurries_equal_weight(self):
        new_slurry = add_slurries((self.slurry1, 1), (self.slurry2, 1))
        rho_expect = (self.slurry1.rhom + self.slurry2.rhom)/2
        self.assertEqual(new_slurry.rhom, rho_expect)

    def test_add_slurries_unequal_weight(self):
        new_slurry = add_slurries((self.slurry1, 0.75), (self.slurry2, 0.33))
        rho_expect = (self.slurry1.rhom*0.75 + self.slurry2.rhom*0.33)/(0.75+0.33)
        self.assertEqual(new_slurry.rhom, rho_expect)


if __name__ == '__main__':
    unittest.main()
