'''
Created on Apr 190 2019

@author: rcriii
'''
import unittest

from DHLLDV import DHLLDV_constants
from DHLLDV import DHLLDV_framework

class Test(unittest.TestCase):

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



