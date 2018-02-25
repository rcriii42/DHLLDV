'''
Test the DHLLDV framework against Sape's excel spreadsheet.
Created on Feb 24, 2018

@author: rcriii
'''
import unittest
import DHLLDV_constants
import DHLLDV_framework
import stratified
import homogeneous

from math import pi, cos, sin

class Test(unittest.TestCase):
    def setUp(self):
        self.rhol = 1.025
        self.nul = 0.0000013
        self.Dp = 0.762
        self.d_med = .5/1000.
        self.d_fine = .2/1000.
        self.epsilon = 0.0000010
        self.rhos = 2.65
        self.Cvs_175 = 0.175
        self.vls_6ms = 6.03
        self.vls_3ms = 3.06
        self.Erhg_obj_3_med = DHLLDV_framework.Cvs_Erhg(self.vls_3ms, self.Dp, self.d_med,
                                                        self.epsilon, self.nul, self.rhol,
                                                        self.rhos, self.Cvs_175, get_dict=True)
        self.Erhg_obj_6_med = DHLLDV_framework.Cvs_Erhg(self.vls_6ms, self.Dp, self.d_med,
                                                        self.epsilon, self.nul, self.rhol,
                                                        self.rhos, self.Cvs_175, get_dict=True)

    def test_carrier_labda_3ms(self):
        Re = homogeneous.pipe_reynolds_number(self.vls_3ms, self.Dp, self.nul)
        self.assertAlmostEqual(homogeneous.swamee_jain_ff(Re, self.Dp, self.epsilon)*10,
                               0.010591687*10,
                               places=5)

    def test_carrier_labda_6ms(self):
        Re = homogeneous.pipe_reynolds_number(self.vls_6ms, self.Dp, self.nul)
        self.assertAlmostEqual(homogeneous.swamee_jain_ff(Re, self.Dp, self.epsilon)*100,
                               0.009558047*100,
                               places=4)

    def test_carrier_il_3ms(self):
        self.assertAlmostEqual(self.Erhg_obj_3_med['il']*100, 0.006633672*100, places=3)

    def test_carrier_il_6ms(self):
        self.assertAlmostEqual(self.Erhg_obj_6_med['il']*10, 0.023246084*10, places=3)

    def test_FB_beta(self):
        """
        test the calculation of beta vs bed fraction (Cv for FB and SB) against Sape's
        iterative scheme
        """
        bed_fraction = self.Cvs_175/DHLLDV_constants.Cvb

        """The following is a direct translation from the VB code in the excel"""
        prediction = bed_fraction*pi
        fraction  = (prediction - sin(prediction)*cos(prediction))/pi
        while abs(bed_fraction - fraction)>.000001:
            prediction = prediction + (bed_fraction - fraction) * pi/2
            fraction = (prediction - sin(prediction) * cos(prediction)) / pi

        self.assertAlmostEqual(stratified.beta(self.Cvs_175), prediction, places=3)

    # def test_fixed_hyd_grad_6ms(self):
    #     il_fb = stratified.fb_head_loss(self.vls_6ms, self.Dp, self.d_med, self.epsilon,
    #                                     self.nul, self.rhol, self.rhos, self.Cvs_175)
    #     self.assertAlmostEqual(il_fb, 0.647189382)
    #
    # def test_fixed_6ms(self):
    #     self.assertAlmostEqual(self.Erhg_obj_6_med['FB'], 2.932702071)#, places=4)
    #
    # def test_fixed_3ms(self):
    #     self.assertAlmostEqual(self.Erhg_obj_3_med['FB'], 0.151968611)#, places=5)

