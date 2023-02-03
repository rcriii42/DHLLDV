"""
Created on Apr 190 2019

@author: rcriii
"""
import math
import unittest


from DHLLDV import DHLLDV_constants
from DHLLDV import DHLLDV_framework
from DHLLDV import DHLLDV_Utils


class Test(unittest.TestCase):
    def setUp(self):
        Dp = 0.5  # Pipe diameter
        d = 1 / 1000.
        epsilon = DHLLDV_constants.steel_roughness
        nu = DHLLDV_constants.water_viscosity[20]
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        # Rsd = (rhos - rhol) / rhol
        Cv = 0.175
        # rhom = Cv * (rhos - rhol) + rhol
        self.GSD = {0: 0.075/1000, 0.15: d/2, 0.5: d, 0.85: d * 2.71}

        self.Cvs_Erhg_obj = DHLLDV_framework.Erhg_graded(self.GSD, 5.0, Dp, epsilon, nu, rhol, rhos, Cv,
                                                         Cvt_eq_Cvs=False, get_dict=True)
        self.Cvt_Erhg_obj = DHLLDV_framework.Erhg_graded(self.GSD, 5.0, Dp, epsilon, nu, rhol, rhos, Cv,
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
        self.assertAlmostEqual(self.Cvs_Erhg_obj['X'], 0.018613909)

    def test_Erhg_graded_fracs(self):
        fs = [0.1166667, 0.1166667, 0.1166667, 0.1166667, 0.1166667,
              0.1166667, 0.1166667, 0.0437954, 0.0437954, 0.0437954, ]
        fs.reverse()
        for i, f in enumerate(fs):
            self.assertAlmostEqual(self.Cvs_Erhg_obj['fracs'][i], f)

    def test_fractions(self):
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
            with self.subTest(msg=f"Testing fraction {i}: {f[0]*100:0.2f}% : {f[1]:0.3}mm"):
                self.assertAlmostEqual(fracs[i], f[0])
            with self.subTest(msg=f"Testing diameter {i}: {f[0]*100:0.2f}% : {f[1]:0.3}mm"):
                self.assertAlmostEqual(ds[i]*1000, f[1])

    def test_large_d15_preserved(self):
        """Test that the d15 is preserved when the pseuodoliquid fraction is negative"""
        Dp = 0.5
        GSD = {0.85: 2.992/1000,
               0.5: 1.1/1000,
               0.15: 0.2368/1000, }
        nu = 0.001005 / (0.9982 * 1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        new_GSD = DHLLDV_framework.create_fracs(GSD, Dp, nu, rhol, rhos)
        log_GSD = DHLLDV_Utils.interpDict(dict((k, math.log10(v)) for k, v in new_GSD.items()))
        logd15 = log_GSD[0.15]
        self.assertAlmostEqual(GSD[0.15]*1000, 10**logd15*1000)

    def test_small_d15_preserved(self):
        """Test that the d15 is preserved when the pseuodoliquid fraction is negative"""
        Dp = 0.5
        GSD = {0.85: 2.448 / 1000,
               0.5: 0.9 / 1000,
               0.15: 0.153 / 1000, }
        nu = 0.001005 / (0.9982 * 1000)
        rhos = 2.65
        rhol = DHLLDV_constants.water_density[20]
        new_GSD = DHLLDV_framework.create_fracs(GSD, Dp, nu, rhol, rhos)
        log_GSD = DHLLDV_Utils.interpDict(dict((k, math.log10(v)) for k, v in new_GSD.items()))
        logd15 = log_GSD[0.15]
        self.assertAlmostEqual(GSD[0.15] * 1000, 10 ** logd15 * 1000)

    def test_Erhg_graded_ds(self):
        ds = [3.7782648, 2.7100000, 1.9437759, 1.3941936, 1.0000000, 0.7937005,
              0.6299605, 0.5000000, 0.2873519, 0.1651423, 0.0949079, ]
        ds.reverse()
        for i, d in enumerate(ds):
            with self.subTest(msg=f"Testing ds[{i}]: {d:0.4f}"):
                self.assertAlmostEqual(self.Cvs_Erhg_obj['ds'][i] * 1000, d)

    def test_ERHG_graded_dx(self):
        dxs = [3.1998590, 2.2951324, 1.6462078, 1.1807598, 0.8908987,
               0.7071068, 0.5612310, 0.3790461, 0.2178393, 0.1251931]
        dxs.reverse()
        for i, d in enumerate(dxs):
            with self.subTest(msg=f"Testing dx[{i}]: {d:0.4f}"):
                self.assertAlmostEqual(self.Cvs_Erhg_obj['dxs'][i] * 1000, d)

    def test_rhox(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['rhox'], 1.004696325)

    def test_Cvs_x(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['Cv_x'], 0.003932876)

    def test_Cvs_r(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['Cv_r'], 0.171742566)

    def test_mu_x(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['mu_x']*10**6,
                               1.0179733E-06*10**6, places=4)

    def test_nu_x(self):
        self.assertAlmostEqual(self.Cvs_Erhg_obj['nu_x']*10**6,
                               1.0132149E-06*10**6, places=4)

    def test_if_Cvt_triggered(self):
        """Just test that the Cvt Erhg is properly triggered"""
        self.assertGreater(self.Cvt_Erhg_obj['Erhg'], self.Cvs_Erhg_obj['Erhg'])


if __name__ == "__main__":
    unittest.main()
