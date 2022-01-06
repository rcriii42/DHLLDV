import unittest

from DHLLDV import SlurryObj

class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.slurry = SlurryObj.Slurry()
        print(self.slurry)

    def test_il(self):
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.il(vls), self.slurry.Erhg_curves['il'][42])
        self.assertEqual(self.slurry.il(vls), self.slurry.im_curves['il'][42])

    def test_Erhg(self):
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.Erhg(vls), self.slurry.Erhg_curves['graded_Cvt_Erhg'][42])

    def test_im(self):
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.im(vls), self.slurry.im_curves['graded_Cvt_im'][42])


if __name__ == '__main__':
    unittest.main()
