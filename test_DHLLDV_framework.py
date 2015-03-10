'''
Created on Mar 4, 2015

@author: rcriii
'''
import unittest
import DHLLDV_constants
import DHLLDV_framework
import stratified

class Test(unittest.TestCase):

    def testCvs_Erhg_obj(self):
        vls = 3.0
        Dp = 0.5
        d=0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        Erhg_obj = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, get_dict=True)
        self.assertAlmostEqual(Erhg_obj['FB'],0.06351955, places=6)
        self.assertAlmostEqual(Erhg_obj['SB'],0.415)
        self.assertAlmostEqual(Erhg_obj['He'],0.0528735)
        self.assertAlmostEqual(Erhg_obj['Ho'],0.0086256283671)
        
    def testCvs_Erhg_result(self):
        vls = 3.0
        Dp = 0.5
        d=0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        Erhg = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        Erhg2 = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(Erhg2, 0.0528735)
        self.assertAlmostEqual(Erhg, 0.0528735)
        
    def testCvs_Erhg_regime(self):
        vls = 3.0
        Dp = 0.5
        d=0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        Erhg_regime = DHLLDV_framework.Cvs_regime(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        Erhg = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(Erhg, 0.0528735)
        self.assertAlmostEqual(Erhg_regime,'heterogeneous')
        
    def testLDV_fig8_11_2(self):
        #stratified.musf = 0.52
#         vls = 0.7
#         Dp = 0.1524
#         d=0.5/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 1.59*rhol+rhol
#         Cvs = 0.2
#         Rsd = (rhos-rhol)/rhol
#         fbot = (2*DHLLDV_constants.gravity*Rsd*Dp)**0.5
#         LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
#         self.assertAlmostEqual(LDV, 1.6/fbot)#, places, msg, delta)
        pass
    
    def testLDV_very_small(self):
        vls = 1
        Dp = 0.5
        d=0.0075/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhol = DHLLDV_constants.water_density[20]
        rhos = 2.65
        Cvs = 0.1
        Rsd = (rhos-rhol)/rhol
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(LDV, 0.8288413, places=4)
        
    def testLDV_small(self):
        vls = 3.5502843557
        Dp = 0.5
        d=0.2/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhol = DHLLDV_constants.water_density[20]
        rhos = 2.65
        Cvs = 0.1
        Rsd = (rhos-rhol)/rhol
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(LDV, 3.5502843557, places=4)
        
    def testLDV_large(self):
        vls = 4.3897193
        Dp = 0.5
        d=0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhol = DHLLDV_constants.water_density[20]
        rhos = 2.65
        Cvs = 0.1
        Rsd = (rhos-rhol)/rhol
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(LDV, 4.3897193, places=5)
         
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
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(LDV, 4.4192975, places=5)
     
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
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=20)
        self.assertAlmostEqual(LDV, 4.0917049, places=5)
        
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
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=20)
        self.assertAlmostEqual(LDV, 1.7689662, places=5) #Gives 1.827
    
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
        LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=20)
        self.assertAlmostEqual(LDV, 2.4907119, places=5)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()