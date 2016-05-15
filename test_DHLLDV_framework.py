'''
Created on Mar 4, 2015

@author: rcriii
'''
import unittest
import DHLLDV_constants
import DHLLDV_framework
#import stratified

class Test(unittest.TestCase):

    def testCvs_Erhg_obj(self):
        vls = 3.0
        Dp = 0.5
        d = 0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        Erhg_obj = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, get_dict=True)
        self.assertAlmostEqual(Erhg_obj['FB'], 0.06351955, places=6)
        self.assertAlmostEqual(Erhg_obj['SB'], 0.415)
        self.assertAlmostEqual(Erhg_obj['He'], 0.2495003)
        self.assertAlmostEqual(Erhg_obj['Ho'], 0.00640100645523)
        
    def testCvs_Erhg_obj2(self):
        #test at a higher velocity to trigger He
        vls = 4.0
        Dp = 0.5
        d = 0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        Erhg_obj = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, get_dict=True)
        self.assertAlmostEqual(Erhg_obj['FB'], 0.11245960, places=6)
        self.assertAlmostEqual(Erhg_obj['SB'], 0.415)
        self.assertAlmostEqual(Erhg_obj['He'], 0.1451765)
        self.assertAlmostEqual(Erhg_obj['Ho'], 0.01051754196773)
    
    def testCvs_Erhg_result(self):
        vls = 3.0
        Dp = 0.5
        d = 0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        Erhg = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(Erhg, 0.06351955, places=6)
        
    def testCvs_Erhg_result2(self):
        #test at a higher velocity to trigger He
        vls = 4.0
        Dp = 0.5
        d = 0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        Erhg = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(Erhg, 0.11245960, places=6)
    
    def testCvs_Erhg_regime(self):
        vls = 3.0
        Dp = 0.5
        d = 0.4/1000
        epsilon = DHLLDV_constants.steel_roughness
        nu = 0.001005/(0.9982*1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Cvs = 0.1
        Erhg_regime = DHLLDV_framework.Cvs_regime(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        Erhg = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(Erhg, 0.06351955, places=6)
        self.assertAlmostEqual(Erhg_regime,'fixed bed')
    
#     def testLDV_fig8_11_2(self):
#         # stratified.musf = 0.52
# #         vls = 0.7
# #         Dp = 0.1524
# #         d=0.5/1000
# #         epsilon = DHLLDV_constants.steel_roughness
# #         nu = 0.001005/(0.9982*1000)
# #         rhol = DHLLDV_constants.water_density[20]
# #         rhos = 1.59*rhol+rhol
# #         Cvs = 0.2
# #         Rsd = (rhos-rhol)/rhol
# #         fbot = (2*DHLLDV_constants.gravity*Rsd*Dp)**0.5
# #         LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
# #         self.assertAlmostEqual(LDV, 1.6/fbot)#, places, msg, delta)
#         pass
#     
#     def testLDV_very_small(self):
#         vls = 1
#         Dp = 0.5
#         d = 0.0075/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvs = 0.1
#         Rsd = (rhos-rhol)/rhol
#         LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
#         self.assertAlmostEqual(LDV, 0.8288413, places=4)
#         
#     def testLDV_small(self):
#         vls = 3.5502843557
#         Dp = 0.5
#         d = 0.2/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvs = 0.1
#         Rsd = (rhos-rhol)/rhol
#         LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
#         self.assertAlmostEqual(LDV, 3.5502843557, places=4)
#         
#     def testLDV_large(self):
#         vls = 4.3897193
#         Dp = 0.5
#         d = 0.4/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvs = 0.1
#         Rsd = (rhos-rhol)/rhol
#         LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
#         self.assertAlmostEqual(LDV, 4.3897193, places=5)
#          
#     def testLDV_large2(self):
#         vls = 4.4226477
#         Dp = 0.5
#         d = 0.8/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvs = 0.1
#         Rsd = (rhos-rhol)/rhol
#         LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
#         self.assertAlmostEqual(LDV, 4.4192975, places=5)
#      
#     def testLDV_drough(self):
#         vls = 4.0917049
#         Dp = 0.5
#         d = 2.1/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvs = 0.1
#         Rsd = (rhos-rhol)/rhol
#         LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=20)
#         self.assertAlmostEqual(LDV, 4.0917049, places=5)
#         
#     def testLDV_SBHe1(self):
#         vls = 1.7689662
#         Dp = 0.5
#         d = 0.8/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvs = 0.0025
#         Rsd = (rhos-rhol)/rhol
#         LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=20)
#         self.assertAlmostEqual(LDV, 1.7689662, places=5) # Gives 1.827
#     
#     def testLDV_SBHe2(self):
#         vls = 2.4907119
#         Dp = 0.5
#         d = 2.1/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvs = 0.0025
#         Rsd = (rhos-rhol)/rhol
#         LDV = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, max_steps=20)
#         self.assertAlmostEqual(LDV, 2.4907119, places=5)
#     
#     def test_Xi_p4(self):
#         vls = 3.0
#         Dp = 0.5
#         d = 0.4/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvt = 0.1
#         Xi = DHLLDV_framework.slip_ratio(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt)
#         self.assertAlmostEqual(Xi, 0.19448177, places=6)
#     
#     def test_Xi_p8(self):
#         vls = 3.0
#         Dp = 0.5
#         d = 0.8/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvt = 0.1
#         Xi = DHLLDV_framework.slip_ratio(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt)
#         self.assertAlmostEqual(Xi, 0.31788144, places=6)
#     
#     def test_fig8_16_4(self):
# #         Dp = 0.762
# #         d = 1.0/1000
# #         epsilon = DHLLDV_constants.steel_roughness
# #         nu = 0.001005/(0.9982*1000)
# #         Rsd = 1.59
# #         rhol = DHLLDV_constants.water_density[20]
# #         rhos = Rsd*rhol+rhol
# #         Cvt = 0.2
# #         print "%4s  %0.5s  %5s"%("vls", "ldv", "Xi")
# #         for vls in [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 5.5, 6.0]:
# #             ldv = DHLLDV_framework.LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt)
# #             Xi = DHLLDV_framework.slip_ratio(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt)
# #             print "%0.3f  %0.3f  %0.4f"%(vls, ldv, Xi)
# #         assert False
#         pass
#     
#     def test_Cvs_from_Cvt_p4(self):
#         vls = 3.0
#         Dp = 0.5
#         d = 0.4/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvt = 0.1
#         Cvs = DHLLDV_framework.Cvs_from_Cvt(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt)
#         self.assertAlmostEqual(Cvs, 0.12414368, places=6)
#     
#     def test_Cvs_from_Cvt_p8(self):
#         vls = 3.0
#         Dp = 0.5
#         d = 0.8/1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhol = DHLLDV_constants.water_density[20]
#         rhos = 2.65
#         Cvt = 0.1
#         Cvs = DHLLDV_framework.Cvs_from_Cvt(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt)
#         self.assertAlmostEqual(Cvs, 0.14660208, places=6)
#     
#     def test_calc_GSD_fractions_057(self):
#         GSD = {0.85:1.20/1000, 0.5:0.35/1000, 0.11:0.075/1000}
#         GSD = DHLLDV_framework.calc_GSD_fractions(GSD, n=1)
#         fracs = sorted(GSD.keys())
#         self.assertAlmostEqual(fracs[0], 0.0752599, places=6)
#         self.assertAlmostEqual(GSD[fracs[0]]*1000, 0.057, places=6)
#     
#     def test_calc_GSD_fractions_057_already_there(self):
#         GSD = {0.85:1.20/1000, 0.5:0.35/1000, 0.11:0.075/1000, .08:.057/1000}
#         GSD = DHLLDV_framework.calc_GSD_fractions(GSD, n=1)
#         fracs = sorted(GSD.keys())
#         self.assertEqual(len(GSD), 4)
#         self.assertAlmostEqual(fracs[0], 0.08, places=6)
#         self.assertAlmostEqual(GSD[fracs[0]]*1000, 0.057, places=6)
#         self.assertAlmostEqual(GSD[.08]*1000, 0.057, places=6)
#     
#     def test_calc_GSD_fractions_others(self):
#         GSD = {0.85: 1.20/1000, 0.5: 0.35/1000, 0.11: 0.075/1000}
#         GSD1 = DHLLDV_framework.calc_GSD_fractions(GSD, n=10)
#         fracs = sorted(GSD1.keys())
#         self.assertAlmostEqual(GSD1[0.5]*1000, 0.35, places=6)
#         self.assertAlmostEqual(GSD1[0.9]*1000, 1.7063602762, places=6)
#         self.assertAlmostEqual(GSD1[0.7]*1000, 0.70769644947624, places=6)
#         self.assertAlmostEqual(GSD1[0.1]*1000, 0.0693032, places=6)
#         
#     def testCvs_Erhg_graded_result(self):
#         vls = 3.0
#         Dp = 0.5
#         GSD = {0.85: 1.20/1000, 0.5: 0.4/1000, 0.11: 0.075/1000}
#         GSD1 = DHLLDV_framework.calc_GSD_fractions(GSD, n=10)
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhos = 2.65
#         rhol = DHLLDV_constants.water_density[20]
#         Cvs = 0.1
#         Erhg = DHLLDV_framework.Cvs_Erhg_graded(vls, Dp, GSD1, epsilon, nu, rhol, rhos, Cvs)
#         self.assertAlmostEqual(Erhg, 0.0871112)
#         
# #     def testCvs_Erhg_graded_result_fig8_16_16(self):
# #         vls = 4.2
# #         Dp = 0.762
# #         GSD = {0.85: 3./1000, 0.5: 1./1000, 0.05: 0.075/1000}
# #         GSD1 = DHLLDV_framework.calc_GSD_fractions(GSD, n=10)
# #         fracs = sorted(GSD1.keys())
# #         print "frac", "d"
# #         for f in fracs:
# #             print f, GSD1[f]*1000
# #         epsilon = DHLLDV_constants.steel_roughness
# #         nu = 0.001005/(0.9982*1000)
# #         rhos = 2.65
# #         rhol = DHLLDV_constants.water_density[20]
# #         Cvs = 0.2
# #         Erhg = DHLLDV_framework.Cvs_Erhg_graded(vls, Dp, GSD1, epsilon, nu, rhol, rhos, Cvs)
# #         self.assertAlmostEqual(Erhg, 0.23)
#         
#     def testCvs_Erhg_graded_result2(self):
#         vls = 3.0
#         Dp = 0.5
#         GSD1 = {0.02: 0.057 / 1000,
#                 0.05: 0.075 / 1000,
#                 0.20: 0.200 / 1000,
#                 0.50: 0.400 / 1000,
#                 0.72: 0.800 / 1000,
#                 0.89: 1.600 / 1000,
#                 0.98: 10.000 / 1000,
#                 0.99: 20.000 / 1000} 
#         fracs = sorted(GSD1.keys())
#         print "frac", "d"
#         for f in fracs:
#             print f, GSD1[f]*1000
#         epsilon = DHLLDV_constants.steel_roughness
#         nu = 0.001005/(0.9982*1000)
#         rhos = 2.65
#         rhol = DHLLDV_constants.water_density[20]
#         Cvs = 0.1
#         Erhg = DHLLDV_framework.Cvs_Erhg_graded(vls, Dp, GSD1, epsilon, nu, rhol, rhos, Cvs)
#         self.assertAlmostEqual(Erhg, 0.1109643)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()