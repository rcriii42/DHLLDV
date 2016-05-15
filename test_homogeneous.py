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
        
    def test_apparent_density(self):
        rhol = DHLLDV_constants.water_density[20]
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        Cvs = 0.25
        self.assertAlmostEqual(homogeneous.apparent_density(rhol, rhos, Cvs, 0.1), 1.039495)
        self.assertAlmostEqual(homogeneous.apparent_density(rhol, rhos, Cvs, 0.5), 1.204675)
        self.assertAlmostEqual(homogeneous.apparent_density(rhol, rhos, Cvs, 1.0), 1.41115)
        
    def test_apparent_viscosity(self):
        rhol = DHLLDV_constants.water_density[20]
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        Cvs = 0.25
        self.assertAlmostEqual(homogeneous.apparent_viscosity(nu, rhol, rhos, Cvs, 0.1)*1.0E+06, 1.0373114)
        self.assertAlmostEqual(homogeneous.apparent_viscosity(nu, rhol, rhos, Cvs, 0.5)*1.0E+06, 1.2440956)
        self.assertAlmostEqual(homogeneous.apparent_viscosity(nu, rhol, rhos, Cvs, 1.0)*1.0E+06, 1.7279746)
        
    def test_apparent_copncentration(self):
        Cvs = 0.25
        self.assertAlmostEqual(homogeneous.apparent_concentration(Cvs, 0.1), 0.225)
        self.assertAlmostEqual(homogeneous.apparent_concentration(Cvs, 0.5), 0.125)
        self.assertAlmostEqual(homogeneous.apparent_concentration(Cvs, 1.0), 0.0)
        
    def test_limiting_particle(self):
        Dp =0.5
        rhol = DHLLDV_constants.water_density[20]
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        self.assertAlmostEqual(homogeneous.limiting_particle(Dp, nu, rhol, rhos)*1000, 0.1061102535055)

    def test_Erhg(self):
        vls = 3.0
        Dp =0.5
        d=0.075/1000
        epsilon = DHLLDV_constants.steel_roughness
        rhol = DHLLDV_constants.water_density[20]
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        Cvs = 0.25
        self.assertAlmostEqual(homogeneous.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs), 0.01187623153019)
        
    def test_head_loss(self):
        vls = 3.0
        Dp = 0.5
        d=0.075/1000
        epsilon = DHLLDV_constants.steel_roughness
        rhol = DHLLDV_constants.water_density[20]
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        Cvs = 0.25
        self.assertAlmostEqual(homogeneous.homogeneous_head_loss(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs), 0.01678936498079)
        self.assertAlmostEqual(homogeneous.homogeneous_pressure_loss(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs), 0.16494432587543)
    
    def test_Erhg_med_sand(self):
        vls = 3.0
        Dp =0.5
        d=0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        rhol = DHLLDV_constants.water_density[20]
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        Cvs = 0.25
        self.assertAlmostEqual(homogeneous.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs), 0.00633356768663)
        
    def test_Erhg_sf(self):
        vls = 3.0
        Dp =0.5
        d=8.0/1000
        epsilon = DHLLDV_constants.steel_roughness
        rhol = DHLLDV_constants.water_density[20]
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        Cvs = 0.25
        self.assertAlmostEqual(homogeneous.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, use_sf=False), 0.00465260820521)
        self.assertAlmostEqual(homogeneous.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs), 0.0302993)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()