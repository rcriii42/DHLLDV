"""Tests of the Wilson Stratified flow regime model,
based on the example and Case Studies in
Slurry Transport Using Centrifugal Pumps, 2nd ed.,
by Wilson, Addie, Sellgren and Clift (WASC2)"""

import unittest

from Wilson import Wilson_Stratified


class MyTestCase(unittest.TestCase):

    def test_vsm_example5_1(self):
        """WASC2, Example 5.1(a), page 112"""
        vsmx_sand = Wilson_Stratified.Vsm_max(0.5, 1.0/1000, .9982, 2.65)
        self.assertAlmostEqual(vsmx_sand, 5.0, delta=0.1)
        vsmx = Wilson_Stratified.Vsm_max(0.5, 1.0/1000, .9982, 1.4)
        self.assertAlmostEqual(vsmx, 2.3, delta=0.1)

    def test_Cvr_max_example5_1(self):
        """WASC2, Example 5.1(b), page 112"""
        cvrmx = Wilson_Stratified.Cvr_max(0.5, 1.0/1000, .9982, 1.4)
        self.assertAlmostEqual(cvrmx, 0.15, delta=.01)

    @unittest.skip('There appears to be an error in WASC2!')
    def test_Vsm_example5_1(self):
        """WASC2, Example 5.1(c), page 112"""
        vs = Wilson_Stratified.Vsm(0.5, 1.0/1000.0, 0.9982, 1.4,
                                   0.4 , 0.24)
        self.assertAlmostEqual(vs, 1.4, places=2)

    def test_vsm_CaseStudy5_1(self):
        """WASC2, Case Study 5.1, page 117"""
        with self.subTest(Dp=0.6):
            vsmx = Wilson_Stratified.Vsm_max(0.6, 0.7/1000, .9982, 2.65)
            self.assertAlmostEqual(vsmx, 5.8, delta=0.1)
            vsmx = Wilson_Stratified.Vsm_max(0.6, 0.7/1000, .9982, 2.65, f=0.012)
            self.assertAlmostEqual(vsmx, 4.65, delta=0.01)
        with self.subTest('Dp = 0.55'):
            vsmx = Wilson_Stratified.Vsm_max(0.55, 0.7 / 1000, .9982, 2.65)
            self.assertAlmostEqual(vsmx, 5.4, delta=0.125)  # Note low precision
            vsmx = Wilson_Stratified.Vsm_max(0.55, 0.7 / 1000, .9982, 2.65, f=0.012)
            self.assertAlmostEqual(vsmx, 4.45, delta=0.01)
        with self.subTest('Dp = 0.65'):
            vsmx = Wilson_Stratified.Vsm_max(0.65, 0.7 / 1000, .9982, 2.65)
            self.assertAlmostEqual(vsmx, 6.1, delta=0.1)
            vsmx = Wilson_Stratified.Vsm_max(0.65, 0.7 / 1000, .9982, 2.65, f=0.012)
            self.assertAlmostEqual(vsmx, 4.84, delta=0.01)

    def test_HeadLoss_CaseStudy5_2(self):
        """WASC2 Case Study 5.2, page 118"""
        im = Wilson_Stratified.stratified_head_loss(4.6, 0.7, 100./1000,
                                                    79.5e-05, 0.00109/1020,
                                                    1.02, 1.790, 0.31, .0714)
        self.assertAlmostEqual(im, 0.0564, delta=.00026)

    def test_PressureLoss_CaseStudy5_2(self):
        """WASC2 Case Study 5.2, page 118"""
        # Note that the viscosity and epsilon were chosen so that if=0.0314 as in WASC2
        p = Wilson_Stratified.stratified_pressure_loss(4.6, 0.7, 100./1000, 79.5e-05,
                                                       0.00109/1020, 1.02, 1.790, 0.31,
                                                       0.0714)
        self.assertAlmostEqual(p, 553./1000, delta=.015)


if __name__ == '__main__':
    unittest.main()
