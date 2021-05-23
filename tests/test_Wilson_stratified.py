import unittest

from Wilson import Wilson_Stratified
from DHLLDV import DHLLDV_constants
from DHLLDV import homogeneous


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.v = 4.4
        self.Dp = 0.6  # Pipe diameter
        self.d = 1 / 1000.
        self.epsilon = DHLLDV_constants.steel_roughness
        self.nu = DHLLDV_constants.water_viscosity[20]
        Re = homogeneous.pipe_reynolds_number(self.v, self.Dp, self.nu)
        self.f = homogeneous.swamee_jain_ff(Re, self.Dp, self.epsilon)
        self.rhos = 2.65
        self.rhol = 0.9982
        self.Cv = 0.08

    def test_vsm_max(self):
        vsmx = Wilson_Stratified.Vsm_max(self.Dp, self.d, self.rhol, self.rhos,
                                         DHLLDV_constants.musf, f=self.f)
        self.assertAlmostEqual(vsmx, 4.640512, places=2)

    def test_Cvr_max(self):
        cvrmx = Wilson_Stratified.Cvr_max(self.Dp, self.d, self.rhol, self.rhos)
        self.assertAlmostEqual(cvrmx, 0.130407, places=3)


    def test_Vsm(self):
        vsm = Wilson_Stratified.Vsm(0.6, 1.0/1000.0, 0.9982, 2.650,
                                    DHLLDV_constants.musf, 0.08, f=self.f)
        self.assertAlmostEqual(vsm, 4.6405122034073*.9999, places=2)


if __name__ == '__main__':
    unittest.main()


