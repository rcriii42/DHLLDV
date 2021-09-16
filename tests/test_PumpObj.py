"""test_PumpObj.py - Tests of the PumpObj

Added by R. Ramsdell 14 September 2021"""

import unittest

from DHLLDV.DHLLDV_Utils import interpDict
from DHLLDV.PumpObj import Pump

class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        H = interpDict({0.357: 30.0930,
                        0.714: 29.4893,
                        1.070: 29.0907,
                        1.427: 28.7819,
                        1.784: 28.4750,
                        2.141: 28.1046,
                        2.497: 27.6276,
                        2.854: 27.0232,
                        3.032: 26.6725,
                        3.211: 26.2916,
                        3.568: 25.4522,
                        3.924: 24.5389,
                        4.281: 23.5957,
                        4.638: 22.6716,
                        4.995: 21.8170,
                        5.351: 21.0824,
                        })
        P = interpDict({0.357: 229.1843,
                        0.714: 344.8400,
                        1.070: 450.4107,
                        1.427: 553.7280,
                        1.784: 656.5711,
                        2.141: 758.8887,
                        2.497: 860.2718,
                        2.854: 960.8030,
                        3.032: 1011.0561,
                        3.211: 1061.6346,
                        3.568: 1165.3520,
                        3.924: 1276.1240,
                        4.281: 1399.6322,
                        4.638: 1542.7293,
                        4.995: 1712.6761,
                        5.351: 1915.6710,
                        })
        self.pump = Pump(name="Test Pump",
                         design_speed=3.5,
                         design_impeller=1.88,
                         suction_dia=0.8636,
                         disch_dia=0.8636,
                         design_QH_curve=H,
                         design_QP_curve=P,
                         avail_power=895,
                         limited="none",
                         )
        self.pump.slurry.fluid = 'fresh'
        self.pump.slurry.rhom = self.pump.slurry.rhol

    def test_efficiency(self):
        """Test the efficiency for the design speed on water"""
        self.assertAlmostEqual(self.pump.efficiency(2.957377), 0.78603, places=3)

    def test_head(self):
        """Test the head for the design speed on water"""
        Q, H, P, N = self.pump.point(2.957377)
        self.assertAlmostEqual(H, 26.82003*self.pump.slurry.rhom, places=2)

    def test_Power(self):
        """Test the power for the design speed on water"""
        Q, H, P, N = self.pump.point(2.957377)
        self.assertAlmostEqual(P, 989.9113*self.pump.slurry.rhom, places=0)

    def test_head_slow(self):
        """Test the head for the a lower speed on water"""
        self.pump.current_speed = 3.377719
        Q, H, P, N = self.pump.point(2.854054)
        self.assertAlmostEqual(H, 24.97872*self.pump.slurry.rhom, places=3)

    def test_power_slow(self):
        """Test the power for the a lower speed on water"""
        self.pump.current_speed = 3.377719
        Q, H, P, N = self.pump.point(2.854054)
        self.assertAlmostEqual(P, 889.7394*self.pump.slurry.rhom, places=0)

    def test_flow_slow(self):
        """Test the return flow for the a lower speed on water"""
        self.pump.current_speed = 3.377719
        Q, H, P, N = self.pump.point(2.854054)
        self.assertAlmostEqual(Q, 2.854054, places=6)

    def test_power_power_limited(self):
        """Test the output point for the power limited case"""
        self.pump.limited = 'power'
        Q, H, P, N = self.pump.point(2.854054)
        with self.subTest(msg='Test the power limited flow'):
            self.assertAlmostEqual(Q, 2.854054, places=6)
        with self.subTest(msg='Test the power limited power'):
            self.assertAlmostEqual(P, 894.84, places=0)



if __name__ == '__main__':
    unittest.main()
