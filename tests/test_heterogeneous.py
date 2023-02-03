'''
Created on Feb 22, 2015

@author: rcriii
'''
import unittest

from DHLLDV import heterogeneous
from DHLLDV import DHLLDV_constants


class Test(unittest.TestCase):

    def test_settlingVelocity(self):
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Rsd = (rhos-rhol)/rhol
        self.assertAlmostEqual(heterogeneous.vt_ruby(0.075/1000, Rsd, nu), 0.0044591)
        self.assertAlmostEqual(heterogeneous.vt_ruby(0.2/1000, Rsd, nu), 0.0256840)
        self.assertAlmostEqual(heterogeneous.vt_ruby(0.4/1000, Rsd, nu), 0.0592375)
        self.assertAlmostEqual(heterogeneous.vt_ruby(0.8/1000, Rsd, nu), 0.1020475)
        self.assertAlmostEqual(heterogeneous.vt_ruby(1.6/1000, Rsd, nu), 0.1549654)
        self.assertAlmostEqual(heterogeneous.vt_ruby(10./1000, Rsd, nu), 0.4018323)
        self.assertAlmostEqual(heterogeneous.vt_ruby(20./1000, Rsd, nu), 0.5691956)

    def test_hinderedSettling(self):
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Rsd = (rhos-rhol)/rhol
        Cvs = 0.1
        self.assertAlmostEqual(heterogeneous.vth_RZ(0.075/1000, Rsd, nu, Cvs), 0.002766062)
        self.assertAlmostEqual(heterogeneous.vth_RZ(0.200/1000, Rsd, nu, Cvs), 0.017171128)
        self.assertAlmostEqual(heterogeneous.vth_RZ(0.400/1000, Rsd, nu, Cvs), 0.042443520)
        self.assertAlmostEqual(heterogeneous.vth_RZ(0.800/1000, Rsd, nu, Cvs), 0.076343479)
        self.assertAlmostEqual(heterogeneous.vth_RZ(1.600/1000, Rsd, nu, Cvs), 0.118563740)
        self.assertAlmostEqual(heterogeneous.vth_RZ(10.000/1000, Rsd, nu, Cvs), 0.313060300)
        self.assertAlmostEqual(heterogeneous.vth_RZ(20.000/1000, Rsd, nu, Cvs), 0.444118731)

    def test_Ehrg_nosf(self):
        vls = 3.0
        Dp = 0.5
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.075/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False, use_sqrtcx=False), 0.0016021)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.2/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False, use_sqrtcx=False), 0.0517285)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.4/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False, use_sqrtcx=False), 0.2495003)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.8/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False, use_sqrtcx=False), 0.4793151)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 1.6/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False, use_sqrtcx=False), 0.6133468)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 10./1000, epsilon, nu, rhol, rhos, Cvs, use_sf=False, use_sqrtcx=False), 0.7417270)

    def test_Ehrg_with_sf(self):
        vls = 3.0
        Dp = 0.5
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.075/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True, use_sqrtcx=False), 0.0016021)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.2/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True, use_sqrtcx=False), 0.0517285)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.4/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True, use_sqrtcx=False), 0.2495003)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 0.8/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True, use_sqrtcx=False), 0.4793151)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 1.6/1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True, use_sqrtcx=False), 0.6133468)
        self.assertAlmostEqual(heterogeneous.Erhg(vls, Dp, 10./1000, epsilon, nu, rhol, rhos, Cvs, use_sf=True, use_sqrtcx=False), 0.6600452)

    def test_head_loss(self):
        vls = 3.0
        Dp = 0.5
        d = 0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        self.assertAlmostEqual(heterogeneous.heterogeneous_head_loss(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, use_sf=False, use_sqrtcx=False)*10, 0.0531630*10)
        self.assertAlmostEqual(heterogeneous.heterogeneous_pressure_loss(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, use_sf=False, use_sqrtcx=False), 0.5204125)


if __name__ == "__main__":
    unittest.main()
