'''
Created on Oct 23, 2014

@author: RCRamsdell
'''

import unittest

from DHLLDV import DHLLDV_Utils


class TestInterpDict(unittest.TestCase):

    def testInstantiateWithDict(self):
        t1 = DHLLDV_Utils.interpDict({0: 0.99984,  # deg C, density in ton/m**3 per wikipedia
                                      4: 0.99997,
                                      5: 0.99996,
                                      10: 0.99970,
                                      15: 0.99910,
                                      20: 0.99820,})
        self.assertAlmostEqual(t1[12.5], (0.9997+0.9991)/2)
        
    def testInterpolation(self):
        t1 = DHLLDV_Utils.interpDict((1, 20), (2, 30), (3, 50))
        self.assertEqual(t1[2.5], 40)
        
    def testBelowRange(self):
        t1 = DHLLDV_Utils.interpDict((1, 20), (2, 30), (3, 50))
        self.assertRaises(IndexError, t1.__getitem__, 19)
        
    def testAboveRange(self):
        t1 = DHLLDV_Utils.interpDict((1, 20), (2, 30), (3, 50))
        self.assertRaises(IndexError, t1.__getitem__, 60)
        
    def testReadOnly(self):
        t1 = DHLLDV_Utils.interpDict((1, 20), (2, 30), (3, 50))
        self.assertRaises(KeyError, t1.__setitem__, 4, 75)

    def test_extrapolate_high(self):
        t1 = DHLLDV_Utils.interpDict((1, 20), (2, 30), (3, 50), extrapolate_high=True)
        self.assertEqual(t1[3.5], 60)

    def test_extrapolate_low(self):
        t1 = DHLLDV_Utils.interpDict((1, 20), (2, 30), (3, 50), extrapolate_low=True)
        self.assertEqual(t1[0.5], 15)


if __name__ == "__main__":
    unittest.main()
