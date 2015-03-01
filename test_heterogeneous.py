'''
Created on Feb 22, 2015

@author: rcriii
'''
import unittest
import heterogeneous
import DHLLDV_constants


class Test(unittest.TestCase):

    def test_settlingVelocity(self):
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Rsd = (rhos-rhol)/rhol
        self.assertAlmostEqual(heterogeneous.vt_grace(0.0075/1000, Rsd, nu), 0.0000249)
        self.assertAlmostEqual(heterogeneous.vt_grace(0.2/1000, Rsd, nu), 0.0134016)#, places=5)
        self.assertAlmostEqual(heterogeneous.vt_grace(0.4/1000, Rsd, nu), 0.0346031)#, places=5)
        self.assertAlmostEqual(heterogeneous.vt_grace(1.6/1000, Rsd, nu), 0.1253364)#, places=4)
        self.assertAlmostEqual(heterogeneous.vt_grace(10./1000, Rsd, nu), 0.3642040, places=2)
        self.assertAlmostEqual(heterogeneous.vt_grace(75./1000, Rsd, nu), 0.9010960, places=1)
        
    def test_Ehrg_nosf(self):
        vls = 3.0
        Dp = 0.5
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.0075/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False), 0.0000051)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.2/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False), 0.0119203)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.4/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False), 0.0528735)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.8/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False), 0.1512408)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 1.6/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False), 0.2493150)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 10./1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False), 0.4106565, places=1)
        
    def test_Ehrg_with_sf(self):
        vls = 3.0
        Dp = 0.5
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.0075/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True), 0.0000051)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.2/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True), 0.0119203)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.4/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True), 0.0528735)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.8/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True), 0.1512408)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 1.6/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True), 0.2493150)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 10./1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True), 0.4117424, places=1)
        
    def test_head_loss(self):
        vls = 3.0
        Dp = 0.5
        d = 0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        self.assertAlmostEqual(heterogeneous.heterogeneous_head_loss(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, use_sf=False), 0.0206256)
        self.assertAlmostEqual(heterogeneous.heterogeneous_pressure_loss(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, use_sf=False), 0.2026330)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()