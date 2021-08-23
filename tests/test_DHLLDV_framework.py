'''
Created on Mar 4, 2015

@author: rcriii
'''
import unittest

from DHLLDV import DHLLDV_constants
from DHLLDV import DHLLDV_framework

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
        DHLLDV_framework.use_sqrtcx = False
        Erhg_obj = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, get_dict=True)
        self.assertAlmostEqual(Erhg_obj['FB'], 0.13631182, places=6)
        self.assertAlmostEqual(Erhg_obj['SB'], 0.415)
        self.assertAlmostEqual(Erhg_obj['He'], 0.2495003)
        self.assertAlmostEqual(Erhg_obj['Ho'], 0.00640100645523)
        DHLLDV_framework.use_sqrtcx = True

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
        DHLLDV_framework.use_sqrtcx = False
        Erhg_obj = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, get_dict=True)
        self.assertAlmostEqual(Erhg_obj['FB'], 0.44104037, places=5)
        self.assertAlmostEqual(Erhg_obj['SB'], 0.415)
        self.assertAlmostEqual(Erhg_obj['He'], 0.1451765)
        self.assertAlmostEqual(Erhg_obj['Ho'], 0.01051754196773)
        DHLLDV_framework.use_sqrtcx = True

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
        self.assertAlmostEqual(Erhg, 0.13631182, places=6)

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
        DHLLDV_framework.use_sqrtcx = False
        Erhg = DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
        self.assertAlmostEqual(Erhg, 0.1451765, places=6)
        DHLLDV_framework.use_sqrtcx = True

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
        self.assertAlmostEqual(Erhg, 0.13631182, places=6)
        self.assertAlmostEqual(Erhg_regime,'fixed bed')

    def test_dlim(self):
        Dp = 0.5
        d = 1.0 / 1000
        nu = 0.001005 / (0.9982 * 1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        self.assertAlmostEqual(DHLLDV_framework.pseudo_dlim(Dp, nu, rhol, rhos)*10**5, 9.4907896)

    def testFractions(self):
        """Test the scheme for dividing the GSD into fractions"""
        Dp = 0.5
        d = 1.0/1000
        GSD = {0.85: d*2.71,
               0.5: d,
               0.15: d/2,
               0: 0.075/1000}
        nu = 0.001005 / (0.9982 * 1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        new_GSD = DHLLDV_framework.create_fracs(GSD, Dp, nu, rhol, rhos)
        fracs = sorted(new_GSD.keys())
        ds = [new_GSD[f] for f in fracs]
        with self.subTest(msg="Test the fraction of the pseudoliquid"):
            self.assertAlmostEqual(fracs[0]*100, 1.8613909)
        with self.subTest(msg="Test the diameter of the pseudoliquid"):
            self.assertAlmostEqual(ds[0]*10**5, 9.4907896)
        with self.subTest(msg="Test the number of points"):
            self.assertEqual(len(fracs), 12)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()