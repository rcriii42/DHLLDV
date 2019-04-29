'''
Created on Apr 190 2019

@author: rcriii
'''
import unittest

from DHLLDV import DHLLDV_constants
from DHLLDV import DHLLDV_framework

class Test(unittest.TestCase):

    def setUp(self):
        self.gsd = {0.85: 1.200 / 1000,
                    0.50: 0.350 / 1000,
                    0.11: 0.075 / 1000, }
        self.gsd2 = DHLLDV_framework.calc_GSD_fractions(self.gsd)

    def test_GSD_min(self):
        """Test the fraction assigned to the grain size that affects viscosity."""
        fracs = sorted(self.gsd2.keys())
        self.assertAlmostEqual(fracs[0], 0.0752599)
        self.assertAlmostEqual(self.gsd2[fracs[0]], 0.057/1000)

    def test_intermediate_diam(self):
        """Test some intermediate values."""
        for k, v in [(0.850000, 1.20000000/1000),
                     (0.800000, 1.00632092/1000),
                     (0.700000, 0.70769645/1000),
                     (0.600000, 0.49768841/1000),
                     (0.500000, 0.35000000/1000),
                     (0.400000, 0.23579134/1000),
                     (0.300000, 0.15885016/1000),
                     (0.200000, 0.10701569/1000),
                     (0.110000, 0.07500000/1000),
                     (0.100000, 0.06930319/1000),]:
            self.assertAlmostEqual(self.gsd2[k], v)

    def test_gsd_max(self):
        """Test the max grain size created."""
        fracs = sorted(self.gsd2.keys())
        self.assertAlmostEqual(fracs[-1], 0.9)
        self.assertAlmostEqual(self.gsd2[fracs[-1]]*1000, 1.70636028)
