import unittest

from DHLLDV import SlurryObj

class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.slurry = SlurryObj.Slurry()
        print(self.slurry)

    def test_il(self):
        vls = self.slurry.vls_list[42]
        self.assertEqual(self.slurry.il(vls), self.slurry.Erhg_curves[42]['il'])


if __name__ == '__main__':
    unittest.main()
