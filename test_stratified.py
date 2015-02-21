'''
Created on Oct 31, 2014

@author: RCRamsdell
'''
import unittest
import stratified
import DHLLDV_constants


class Test(unittest.TestCase):

    def test_beta(self):
        self.assertAlmostEqual(stratified.beta(0.10), 0.98392901, places=4)

    def test_areas(self):
        Ap, A1, A2 = stratified.areas(0.5, 0.1)
        self.assertAlmostEqual(Ap, 0.1963495)
        self.assertAlmostEqual(A1, 0.1636246)
        self.assertAlmostEqual(A2, 0.0327249)

    def test_perimeters(self):
        Op, O1, O12, O2 = stratified.perimeters(0.5, 0.1)
        self.assertAlmostEqual(Op, 1.5707963)
        #Reduced precision because Beta only to 4 places
        self.assertAlmostEqual(O1, 1.0788463, places=4)
        self.assertAlmostEqual(O12, 0.4163317, places=4)
        self.assertAlmostEqual(O2, 0.4919500, places=4)

    def test_lambda1(self):
        Ap, A1, A2 = stratified.areas(0.5, 0.1)
        Op, O1, O12, O2 = stratified.perimeters(0.5, 0.1)
        Dp_H = 4*A1/(O1+O12)
        v1 = 2*Ap/A1
        epsilon = DHLLDV_constants.steel_roughness
        nu_l = DHLLDV_constants.water_viscosity[20]
        self.assertAlmostEqual(stratified.lambda1(Dp_H, v1, epsilon, nu_l), 
                               0.01349789)
    
    def test_lambda12(self):
        Ap, A1, A2 = stratified.areas(0.5, 0.1)
        Op, O1, O12, O2 = stratified.perimeters(0.5, 0.1)
        Dp_H = 4*A1/(O1+O12)
        v1 = 2*Ap/A1
        v2 = 0.0
        d = 0.3
        nu_l = DHLLDV_constants.water_viscosity[20]
        self.assertAlmostEqual(stratified.lambda12(Dp_H, d, v1, v2, nu_l), 
                               0.46554005, places=5)
    
    def test_lambda12_sf(self):
        Ap, A1, A2 = stratified.areas(0.5, 0.1)
        Op, O1, O12, O2 = stratified.perimeters(0.5, 0.1)
        Dp_H = 4*A1/(O1+O12)
        d=0.3
        v1 = 2*Ap/A1
        v2 = 0.0
        epsilon = DHLLDV_constants.steel_roughness
        nu_l = DHLLDV_constants.water_viscosity[20]
        rho_s = 2.65
        rho_l = DHLLDV_constants.water_density[20]
        self.assertAlmostEqual(stratified.lambda12_sf(Dp_H, d, v1, v2, epsilon, nu_l, rho_l, rho_s),
                               0.09045342, places=6)
    
    def test_fb_pressure_loss(self):
        vls = 2.0
        Dp = 0.5
        d = 0.3
        epsilon = DHLLDV_constants.steel_roughness
        nu_l = DHLLDV_constants.water_viscosity[20]
        rho_s = 2.65
        rho_l = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        self.assertAlmostEqual(stratified.fb_pressure_loss(vls, Dp, d, epsilon, nu_l, rho_l, rho_s, Cvs),
                               0.22937437, places=5)
        self.assertAlmostEqual(stratified.fb_head_loss(vls, Dp, d, epsilon, nu_l, rho_l, rho_s, Cvs),
                               0.02334757, places=6)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
