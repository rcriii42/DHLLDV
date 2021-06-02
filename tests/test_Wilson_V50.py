"""Tests of the Wilson Stratified flow regime model,
based on the example and Case Studies in
Slurry Transport Using Centrifugal Pumps, 2nd ed.,
by Wilson, Addie, Sellgren and Clift (WASC2)"""

import unittest
import Wilson.Wilson_V50
import DHLLDV.DHLLDV_constants


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.epsilon = DHLLDV.DHLLDV_constants.steel_roughness
        self.nu = 1.003e-06 #DHLLDV.DHLLDV_constants.water_viscosity[20]
        self.rhol = 0.9982 #DHLLDV.DHLLDV_constants.water_density[20]
        self.rhos = 2.65
        self.musf = 0.4

    def test_w_CaseStudy6_1a(self):
        """Test based on WASC Case Study 6.1, page 145"""
        with self.subTest(d=0.7):
            w50 = Wilson.Wilson_V50.w(0.7/1000, self.nu, self.rhol, self.rhos)
            self.assertAlmostEqual(w50, 0.127, places=1)
        with self.subTest(d=1):
            w50 = Wilson.Wilson_V50.w(1/1000, self.nu, self.rhol, self.rhos)
            self.assertAlmostEqual(w50, 0.1486, places=1)

    def test_sigma_CaseStudy6_1a(self):
        """Test based on WASC Case Study 6.1, page 145"""
        sigma = Wilson.Wilson_V50.sigma(0.65, 0.7/1000, 1.0/1000, self.nu, self.rhol, self.rhos)
        self.assertAlmostEqual(sigma, 0.069, places=1)

    def test_M_CaseStudy6_1a(self):
        """Test based on WASC Case Study 6.1, page 145"""
        M = Wilson.Wilson_V50.M(0.65, 0.7/1000, 1.0/1000, self.nu, self.rhol, self.rhos)
        self.assertAlmostEqual(M, 1.7, places=3)

    def test_V50_CaseStudy6_1a(self):
        """Test based on WASC Case Study 6.1, page 145"""
        _v50 = Wilson.Wilson_V50.V50(0.65, 0.7/1000, 1.0/1000, self.epsilon, self.nu, self.rhol, self.rhos)
        self.assertAlmostEqual(_v50, 3.47, places=0)

    def test_head_loss_CaseStudy6_1a(self):
        """Test based on WASC Case Study 6.1, page 145"""
        im = Wilson.Wilson_V50.heterogeneous_head_loss(6.3, 0.65, 0.7/1000, 1.0/1000,
                                                           self.epsilon, self.nu, self.rhol,
                                                           self.rhos, 0.2, self.musf)
        self.assertAlmostEqual(im, 0.0612, places=1)


if __name__ == '__main__':
    unittest.main()
