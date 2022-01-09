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

    # Test all the setters and getters and auto-updating of curves
    def test_fluid(self):
        self.assertEqual(self.slurry.fluid, 'fresh')

    def test_fluid_changed(self):
        """Test that changing the fluid triggers changing the curves

        Also tests that Erhg curves auto-update"""
        self.slurry.generate_curves()  # Make sure the curves were up-to-date
        self.assertFalse(self.slurry.curves_dirty)  # generating curves should set this false
        erhg_il = self.slurry.Erhg_curves['il'][42]
        self.slurry.fluid = 'salt'
        self.assertTrue(self.slurry.curves_dirty)  # Curves should be dirty after updating the fluid
        self.assertNotEqual(self.slurry.Erhg_curves['il'][42], erhg_il)  # should have changed
        self.slurry.fluid = 'fresh'
        self.assertTrue(self.slurry.curves_dirty)  # Curves should be dirty after updating the fluid
        self.assertEqual(self.slurry.Erhg_curves['il'][42], erhg_il)  # should have changed back

    def test_epsilon_changed(self):
        """Test that changing epsilon triggers changes in the curves

        Also tests that im_curves auto-update"""
        self.slurry.generate_curves()               # Make sure the curves were up-to-date
        self.assertFalse(self.slurry.curves_dirty)  # generating curves should set this false
        il = self.slurry.im_curves['il'][42]
        self.slurry.epsilon = 4.0e-05
        self.assertTrue(self.slurry.curves_dirty)   # Curves should be dirty after updating epsilon
        self.assertNotEqual(self.slurry.im_curves['il'][42], il)    # The value of il for that velocity
                                                                    # should have changed

    def test_rhos_changed(self):
        """Test that the curves are regenerated after changing rhos

        Also tests that LDV curves auto-update"""
        self.slurry.generate_curves()               # Make sure the curves were up-to-date
        self.assertFalse(self.slurry.curves_dirty)  # generating curves should set this false
        ldv_im = self.slurry.LDV_curves['im'][21]
        ldv85_im = self.slurry.LDV85_curves['im'][11]
        self.slurry.rhos = 3.0
        self.assertTrue(self.slurry.curves_dirty)  # Curves should be dirty after updating rhos
        self.assertNotEqual(self.slurry.LDV_curves['im'][21], ldv_im)
        self.assertNotEqual(self.slurry.LDV85_curves['im'][11], ldv85_im)

    def test_max_index_changed(self):
        self.slurry.generate_curves()               # Make sure the curves were up-to-date
        self.assertFalse(self.slurry.curves_dirty)  # generating curves should set this false
        vmax = max(self.slurry.vls_list)
        self.slurry.max_index = 50
        self.assertTrue(self.slurry.curves_dirty)  # Curves should be dirty after updating max_index
        self.assertNotEqual(max(self.slurry.vls_list), vmax)  # The maximum velocity is tied to the max_index


if __name__ == '__main__':
    unittest.main()
