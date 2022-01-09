import unittest

from DHLLDV import SlurryObj

class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.slurry = SlurryObj.Slurry()
        self.slurry.fluid = 'fresh'
        self.slurry.Dp = 0.5

    def test_Cvi(self):
        cvi = (1.287265 - 0.9982)/(1.92 - 0.9982)
        self.assertAlmostEqual(self.slurry.Cvi, cvi)

    def test_dx_1mm(self):
        """Test the calculation of GSD for 1mm D50"""
        self.assertAlmostEqual(self.slurry.get_dx(0.10)*1000, 0.4528618)
        self.assertAlmostEqual(self.slurry.get_dx(0.15)*1000, 0.50)
        self.assertAlmostEqual(self.slurry.get_dx(0.42)*1000, 0.8534796)
        self.assertAlmostEqual(self.slurry.get_dx(0.50)*1000, 1.0)
        self.assertAlmostEqual(self.slurry.get_dx(0.69)*1000, 1.7215072)
        self.assertAlmostEqual(self.slurry.get_dx(0.85)*1000, 2.72)

    def test_dx_0p22mm(self):
        """Test the calculation of GSD for 0.22mm D50

        This tests the case where the Xmin > 0.1"""
        s = SlurryObj.Slurry()
        s.D50 = 0.22/1000
        self.assertAlmostEqual(min(s.GSD.keys()), 0.156748040)
        self.assertAlmostEqual(s.get_dx(0.10)*1000, 0.0996296)
        self.assertAlmostEqual(s.get_dx(0.15)*1000, 0.11)
        self.assertAlmostEqual(s.get_dx(0.42)*1000, 0.1877655)
        self.assertAlmostEqual(s.get_dx(0.50)*1000, 0.22)
        self.assertAlmostEqual(s.get_dx(0.69)*1000, 0.3787316)
        self.assertAlmostEqual(s.get_dx(0.85)*1000, 0.598400)

    def test_il_fresh(self):
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.il(vls), self.slurry.Erhg_curves['il'][42])
        self.assertEqual(self.slurry.il(vls), self.slurry.im_curves['il'][42])

    def test_il_salt(self):
        self.slurry.fluid = 'salt'
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.il(vls), self.slurry.Erhg_curves['il'][42])
        self.assertEqual(self.slurry.il(vls), self.slurry.im_curves['il'][42])

    def test_Erhg_fresh(self):
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.Erhg(vls), self.slurry.Erhg_curves['graded_Cvt_Erhg'][42])

    def test_Erhg_salt(self):
        self.slurry.fluid = 'salt'
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.Erhg(vls), self.slurry.Erhg_curves['graded_Cvt_Erhg'][42])

    def test_im_fresh(self):
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.im(vls), self.slurry.im_curves['graded_Cvt_im'][42])

    def test_im_salt(self):
        self.slurry.fluid = 'salt'
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.im(vls), self.slurry.im_curves['graded_Cvt_im'][42])


if __name__ == '__main__':
    unittest.main()
