'''
Created on Oct 7, 2014

@author: RCRamsdell

Testing the homogeneous module and water constants
'''
import unittest
import homogeneous
import DHLLDV_constants


class Test(unittest.TestCase):

    def test_water_density(self):
        self.assertEqual(DHLLDV_constants.water_density[20], 0.9982)

    def test_water_dynamic_viscosity(self):
        self.assertEqual(DHLLDV_constants.water_dynamic_viscosity[20], 0.001005)

    def test_water_kinematic_viscosity(self):
        self.assertEqual(DHLLDV_constants.water_viscosity[20], 0.001005/(0.9982*1000))

    def test_pipe_reynolds_number(self):
        nu = DHLLDV_constants.water_viscosity[20]
        self.assertAlmostEqual(homogeneous.pipe_reynolds_number(3.0, 0.5, nu), 1489850.746, places=3)

    def test_swamee_jain(self):
        nu = DHLLDV_constants.water_viscosity[20]
        Re = homogeneous.pipe_reynolds_number(3.0, 0.5, nu)
        lmbda = homogeneous.swamee_jain_ff(Re, 0.5, DHLLDV_constants.steel_roughness)
        self.assertAlmostEqual(lmbda, 0.0129407)
        Re = 2320  #laminar
        lmbda = homogeneous.swamee_jain_ff(Re, 0.5, DHLLDV_constants.steel_roughness)
        self.assertAlmostEqual(lmbda, 2.75862069e-02)

    def test_Erhg(self):
        vls = 3.0
        Dp =0.5
        epsilon = DHLLDV_constants.steel_roughness
        rhol = DHLLDV_constants.water_density[20]
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        Cvs = 0.25
        self.assertAlmostEqual(homogeneous.Erhg(vls, Dp, epsilon, nu, rhol, rhos, Cvs), 0.00843819592638)
        
    def test_head_loss(self):
        vls = 3.0
        Dp = 0.5
        epsilon = DHLLDV_constants.steel_roughness
        rhol = DHLLDV_constants.water_density[20]
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        Cvs = 0.25
        self.assertAlmostEqual(homogeneous.homogeneous_head_loss(vls, Dp, epsilon, nu, rhol, rhos, Cvs), 0.01536706804371)
        self.assertAlmostEqual(homogeneous.homogeneous_pressure_loss(vls, Dp, epsilon, nu, rhol, rhos, Cvs), 0.15097120600165)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()