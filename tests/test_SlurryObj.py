import unittest

from DHLLDV import SlurryObj

class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.slurry = SlurryObj.Slurry()
        self.slurry.fluid = 'fresh'
        self.slurry.Dp = 0.5
        self.slurry.generate_curves()

    def test_dx_10(self):
        """Test the calculation of d10"""
        self.assertAlmostEqual(self.slurry.get_dx(0.10)*1000, 0.4528618)

    def test_dx_15(self):
        """Test the calculation of d15"""
        self.assertAlmostEqual(self.slurry.get_dx(0.15)*1000, 0.50)

    def test_dx_42(self):
        """Test the calculation of d42"""
        self.assertAlmostEqual(self.slurry.get_dx(0.42)*1000, 0.8534796)
    def test_dx50(self):
        """Test the calculation of d50"""
        self.assertAlmostEqual(self.slurry.get_dx(0.50) * 1000, 1.0)

    def test_dx_69(self):
        """Test the calculation of d69"""
        self.assertAlmostEqual(self.slurry.get_dx(0.69)*1000, 1.7215072)

    def test_dx85(self):
        """Test the calculation of d85"""
        self.assertAlmostEqual(self.slurry.get_dx(0.85) * 1000, 2.72)

    def test_il_fresh(self):
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.il(vls), self.slurry.Erhg_curves['il'][42])
        self.assertEqual(self.slurry.il(vls), self.slurry.im_curves['il'][42])

    def test_il_salt(self):
        self.slurry.fluid = 'salt'
        self.slurry.generate_curves()
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.il(vls), self.slurry.Erhg_curves['il'][42])
        self.assertEqual(self.slurry.il(vls), self.slurry.im_curves['il'][42])

    def test_Erhg_fresh(self):
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.Erhg(vls), self.slurry.Erhg_curves['graded_Cvt_Erhg'][42])

    def test_Erhg_salt(self):
        self.slurry.fluid = 'salt'
        self.slurry.generate_curves()
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.Erhg(vls), self.slurry.Erhg_curves['graded_Cvt_Erhg'][42])

    def test_im_fresh(self):
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.im(vls), self.slurry.im_curves['graded_Cvt_im'][42])

    def test_im_salt(self):
        self.slurry.fluid = 'salt'
        self.slurry.generate_curves()
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.im(vls), self.slurry.im_curves['graded_Cvt_im'][42])


if __name__ == '__main__':
    unittest.main()
