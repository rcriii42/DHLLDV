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
        self.Cvt_Erhg_obj = DHLLDV_framework.Erhg_graded(GSD, 5.0, Dp, epsilon, nu, rhol, rhos, Cv,
                                                         Cvt_eq_Cvs=True, get_dict=True)

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
        with self.subTest(msg="Test the number of points"):
            self.assertEqual(len(fracs), 11)
            for i, f in enumerate([(1.86139090E-02, 9.4907896E-02),
                                   (6.24092727E-02, 1.6514226E-01),
                                   (1.06204636E-01, 2.8735193E-01),
                                   (1.50000000E-01, 5.0000000E-01),
                                   (2.66666667E-01, 6.2996052E-01),
                                   (3.83333333E-01, 7.9370053E-01),
                                   (5.00000000E-01, 1.0000000E+00),
                                   (6.16666667E-01, 1.3941936E+00),
                                   (7.33333333E-01, 1.9437759E+00),
                                   (8.50000000E-01, 2.7100000E+00),
                                   (9.66666667E-01, 3.7782648E+00),
                                   ]):
                with self.subTest(msg = f"Testing fraction {i}: {f[0]*100:0.2f}% : {f[1]:0.3}mm"):
                    self.assertAlmostEqual(fracs[i], f[0])
                with self.subTest(msg = f"Testing diameter {i}: {f[0]*100:0.2f}% : {f[1]:0.3}mm"):
                    self.assertAlmostEqual(ds[i]*1000, f[1])


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


    def test_if_Cvt_triggered(self):
        """Just test that the Cvt Erhg is properly triggered"""
        self.assertGreater(self.Cvt_Erhg_obj['Erhg'], self.Cvs_Erhg_obj['Erhg'])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()