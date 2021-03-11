'''
Created on Apr 190 2019

@author: rcriii
'''
import unittest

from DHLLDV import DHLLDV_constants
from DHLLDV import DHLLDV_framework

class Test(unittest.TestCase):
    def setUp(self):
        Dp = 0.762  # Pipe diameter
        d = 1 / 1000.
        epsilon = DHLLDV_constants.steel_roughness
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        Rsd = (rhos - rhol) / rhol
        Cv = 0.175
        rhom = Cv * (rhos - rhol) + rhol
        GSD = {0.11: 0.075 / 1000, 0.5: d, 0.85: d * 2.71}

        self.Cvs_Erhg_obj = DHLLDV_framework.Erhg_graded(GSD, 5.0, Dp, epsilon, nu, rhol, rhos, Cv,
                                                         Cvt_eq_Cvs=False, get_dict=True)

    def test_dlim_500(self):
        """Test the dlim for 500mm pipe"""
        dlim = DHLLDV_framework.pseudo_dlim(0.50,
                                            DHLLDV_constants.water_viscosity[20],
                                            DHLLDV_constants.water_density[20],
                                            2.65)
        self.assertAlmostEqual(9.4907896, dlim * 10**5)


    def test_dlim_762(self):
        """Test the dlim for 762mm pipe"""
        dlim = DHLLDV_framework.pseudo_dlim(0.762,
                                            DHLLDV_constants.water_viscosity[20],
                                            DHLLDV_constants.water_density[20],
                                            2.65)
        self.assertAlmostEqual(1.0769557, dlim * 10 ** 4)

    def test_Erhg_graded_X(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['X'], 0.16447698)

    def test_Erhg_graded_fracs(self):
        fs = [1.00000000, 0.91644770, 0.83289540, 0.74934309, 0.66579079,
              0.58223849, 0.49868619, 0.41513388, 0.33158158, 0.24802928,
              0.16447698]
        fs.reverse()
        for i, f in enumerate(fs):
            self.assertAlmostEqual(self.Cvs_Erhg_obj['fracs'][i], f)


    def test_Erhg_graded_ds(self):
        ds = [4.1545841, 3.2746792, 2.5811304, 2.0344693, 1.6035863,
              1.2639606, 0.9913120, 0.5691244, 0.3267413, 0.1875862,
              0.1076956]
        ds.reverse()
        for i, d in enumerate(ds):
            self.assertAlmostEqual(self.Cvs_Erhg_obj['ds'][i] * 1000, d)


    def test_ERHG_graded_dx(self):
        dxs = [3.688486149, 2.907296691, 2.291556403, 1.806224581, 1.42368184,
              1.119365591, 0.751119082, 0.431226721, 0.247572574, 0.142134466]
        dxs.reverse()
        for i, d in enumerate(dxs):
            self.assertAlmostEqual(self.Cvs_Erhg_obj['dxs'][i] * 1000, d)

    def test_rhox(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['rhox'], 1.05388688)


    def test_Cvs_x(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['Cv_x'], 0.033712847)


    def test_Cvs_r(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['Cv_r'], 0.146216529)


    def test_mu_x(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['mu_x'] * 10 ** 6, 1.1059845)


    def test_nu_x(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['nu_x'] * 10 ** 6, 1.0494338)
