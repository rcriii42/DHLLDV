'''
Created on Oct 31, 2014

@author: RCRamsdell
'''
import unittest
import stratified

class Test(unittest.TestCase):

    def testBeta(self):
        self.assertAlmostEqual(stratified.beta(0.10), 0.98392901, places=4)

    def testAreas(self):
        Ap, A1, A2 = stratified.areas(0.5, 0.1)
        self.assertAlmostEqual(Ap, 0.1963495)
        self.assertAlmostEqual(A1, 0.1636246)
        self.assertAlmostEqual(A2, 0.0327249)
        
    def testPerimeters(self):
        Op, O1, O12, O2 = stratified.perimeters(0.5, 0.1)
        self.assertAlmostEqual(Op, 1.5707963)
        self.assertAlmostEqual(O1, 1.0788463, places=4) #Reduced precision because Beta only to 4 places
        self.assertAlmostEqual(O12, 0.4163317, places=4)
        self.assertAlmostEqual(O2, 0.4919500, places=4)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()