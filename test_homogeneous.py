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

    def test_pressure_losses(self):
        nu = DHLLDV_constants.water_viscosity[20]
        rhol = DHLLDV_constants.water_density[20]
        epsilon = DHLLDV_constants.steel_roughness
        delta_p = homogeneous.fluid_pressure_loss(3.0, 0.5, epsilon, nu, rhol)
        self.assertAlmostEqual(delta_p, 0.1162564)
        il = homogeneous.fluid_head_loss(3.0, 0.5, epsilon, nu, rhol)
        self.assertAlmostEqual(il, 0.01187623)

    def test_relative_viscosity(self):
        Cvs = 0.25
        self.assertAlmostEqual(homogeneous.relative_viscosity(Cvs), 2.4262998)

    def test_homogeneous_pressure_losses(self):
        Cvs = 0.25
        nu = DHLLDV_constants.water_viscosity[20]
        rhol = DHLLDV_constants.water_density[20]
        epsilon = DHLLDV_constants.steel_roughness
        delta_pm = homogeneous.homogeneous_pressure_loss(3.0, 0.5, epsilon, nu, rhol, Cvs)
        self.assertAlmostEqual(delta_pm, 1.258881141e-01)
        im = homogeneous.homogeneous_head_loss(3.0, 0.5, epsilon, nu, rhol, Cvs)
        self.assertAlmostEqual(im, 1.286016339e-02)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()