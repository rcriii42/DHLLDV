"""
Created on Apr 29, 2019

@author: rcriii
"""

import unittest

from DHLLDV import DHLLDV_constants
from DHLLDV import DHLLDV_framework

class Test(unittest.TestCase):


    def testLDV_very_small(self):
        vls = 1
        Dp = 0.5
        d = 0.01/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhol = DHLLDV_constants.water_density[20]
        rhos = 2.65
        Cvs = 0.1
        Rsd = (rhos-rhol)/rhol
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(LDV, 0.8288413, places=4)
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=100)
        self.assertAlmostEqual(LDV, 0.8288413, places=6)

    def testLDV_small(self):
        vls = 4.17
        Dp = 0.5
        d = 0.15/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhol = DHLLDV_constants.water_density[20]
        rhos = 2.65
        Cvs = 0.1
        Rsd = (rhos-rhol)/rhol
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(LDV, 3.6732778916, places=4)
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=100)
        self.assertAlmostEqual(LDV, 3.6732778916, places=5)

    def testLDV_large(self):
        vls = 4.3897193
        Dp = 0.5
        d = 0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhol = DHLLDV_constants.water_density[20]
        rhos = 2.65
        Cvs = 0.1
        Rsd = (rhos-rhol)/rhol
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(LDV, 4.9492960, places=4)
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=100)
        self.assertAlmostEqual(LDV, 4.9492960, places=5)

    def testLDV_large2(self):
        vls = 4.4226477
        Dp = 0.5
        d = 0.8/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhol = DHLLDV_constants.water_density[20]
        rhos = 2.65
        Cvs = 0.1
        Rsd = (rhos-rhol)/rhol
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=100)
        self.assertAlmostEqual(LDV, 4.8456347, places=5)
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)#, max_steps=100)
        self.assertAlmostEqual(LDV, 4.8456347, places=4)
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=5)
        self.assertAlmostEqual(LDV, 4.8456347, places=3)

    def testLDV_drough(self):
        vls = 4.0917049
        Dp = 0.5
        d = 2.1/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhol = DHLLDV_constants.water_density[20]
        rhos = 2.65
        Cvs = 0.1
        Rsd = (rhos-rhol)/rhol
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=100)
        self.assertAlmostEqual(LDV, 4.3325182, places=5)
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(LDV, 4.3325182, places=4)

    def testLDV_SBHe1(self):
        vls = 1.7689662
        Dp = 0.5
        d = 0.8/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhol = DHLLDV_constants.water_density[20]
        rhos = 2.65
        Cvs = 0.0025
        Rsd = (rhos-rhol)/rhol
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=100)
        self.assertAlmostEqual(LDV, 3.2844888, places=5)
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(LDV, 3.2844888, places=3)

    def testLDV_SBHe2(self):
        vls = 2.4907119
        Dp = 0.5
        d = 2.1/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhol = DHLLDV_constants.water_density[20]
        rhos = 2.65
        Cvs = 0.0025
        Rsd = (rhos-rhol)/rhol
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=100)
        self.assertAlmostEqual(LDV, 3.8770674, places=5)
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(LDV, 3.8770674, places=3)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()