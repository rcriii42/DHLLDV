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
        self.Erhg_obj_6_med = DHLLDV_framework.Cvs_Erhg(6.03, self.Dp, self.d_med, self.epsilon, self.nul,
                                                        self.rhol, self.rhos, self.Cvs_175, get_dict=True)
        self.Erhg_obj_3_med = DHLLDV_framework.Cvs_Erhg(3.06, self.Dp, self.d_med, self.epsilon, self.nul,
                                                        self.rhol, self.rhos, self.Cvs_175, get_dict=True)

    def test_carrier_il_6ms(self):
        self.assertAlmostEqual(self.Erhg_obj_6_med['il'], 0.023246084, places=4)

    def test_carrier_il_3ms(self):
        self.assertAlmostEqual(self.Erhg_obj_3_med['il'], 0.006633672, places=5)

    def test_fixed_6ms(self):
        self.assertAlmostEqual(self.Erhg_obj_6_med['FB'], 3.536214758)#, places=4)

    def test_fixed_3ms(self):
        self.assertAlmostEqual(self.Erhg_obj_3_med['FB'], 0.17636064)#, places=5)

