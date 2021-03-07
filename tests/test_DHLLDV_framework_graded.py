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
        # self.gsd500 = DHLLDV_framework.add_dlim_to_GSD(self.gsd,
        #                                                0.50,
        #                                                DHLLDV_constants.water_viscosity[20],
        #                                                DHLLDV_constants.water_density[20],
        #                                                2.65)
        # self.gsd762 = DHLLDV_framework.add_dlim_to_GSD(self.gsd,
        #                                                0.762,
        #                                                DHLLDV_constants.water_viscosity[20],
        #                                                DHLLDV_constants.water_density[20],
        #                                                2.65)
        self.gsd2 = DHLLDV_framework.calc_GSD_fractions(self.gsd)

    def test_dlim_500(self):
        """Test the dlim for 500mm pipe"""
        dlim = DHLLDV_framework.pseudo_dlim(0.50,
                                            DHLLDV_constants.water_viscosity[20],
                                            DHLLDV_constants.water_density[20],
                                            2.65)
        self.assertAlmostEqual(9.4907896, dlim * 10**5)


    def test_dlim_762(self):
        """Test the dlim for 762mm pipe"""
        dlim = DHLLDV_framework.pseudo_dlim(0.762,
                                            DHLLDV_constants.water_viscosity[20],
                                            DHLLDV_constants.water_density[20],
                                            2.65)
        self.assertAlmostEqual(1.0769557, dlim * 10 ** 4)


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
