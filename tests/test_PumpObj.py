"""test_PumpObj.py - Tests of the PumpObj

Added by R. Ramsdell 14 September 2021"""

import unittest

from DHLLDV.DHLLDV_Utils import interpDict
from DHLLDV.PumpObj import Pump
from DHLLDV.DriverObj import Driver


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        H = interpDict({0.3567568: 30.093008,
                        0.7135136: 29.489334,
                        1.0702704: 29.090661,
                        1.4270272: 28.781914,
                        1.7837840: 28.474970,
                        2.1405408: 28.104580,
                        2.4972976: 27.627627,
                        2.8540544: 27.023164,
                        3.0324328: 26.672462,
                        3.2108112: 26.291587,
                        3.5675680: 25.452159,
                        3.9243248: 24.538921,
                        4.2810816: 23.595749,
                        4.6378384: 22.671603,
                        4.9945952: 21.816991,
                        5.3513520: 21.082392,
                        })
        P = interpDict({0.356757: 229.184279,
                        0.713514: 344.839984,
                        1.070270: 450.410668,
                        1.427027: 553.727956,
                        1.783784: 656.571060,
                        2.140541: 758.888651,
                        2.497298: 860.271806,
                        2.854054: 960.803020,
                        3.032433: 1011.056064,
                        3.210811: 1061.634585,
                        3.567568: 1165.351961,
                        3.924325: 1276.124040,
                        4.281082: 1399.632204,
                        4.637838: 1542.729293,
                        4.994595: 1712.676097,
                        5.351352: 1915.670989,
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

    def test_power_required(self):
        """Test the power required for the design speed on water"""
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
            self.assertAlmostEqual(P, 894.97, places=2)
        with self.subTest(msg='Test the power limited head'):
            self.assertAlmostEqual(H, 25.131, places=3)

    def test_power_torque_limited(self):
        """Test the output point for the power limited case"""
        self.pump.limited = 'torque'
        Q, H, P, N = self.pump.point(3.03243)
        with self.subTest(msg='Test the torque limited flow'):
            self.assertAlmostEqual(Q, 3.03243, places=6)
        with self.subTest(msg='Test the torque limited power'):
            self.assertAlmostEqual(P, 805.0921, places=2)
        with self.subTest(msg='Test the torque limited head'):
            self.assertAlmostEqual(H, 20.928, places=3)

    def test_power_avail_power_limited(self):
        """Test the right result for the power limited case"""
        self.pump.limited = 'power'
        self.assertAlmostEqual(self.pump.power_available(3.0), 895)

    def test_power_avail_torque_limited(self):
        """Test the right result for the torque limited case"""
        self.pump.limited = 'torque'
        self.assertAlmostEqual(self.pump.power_available(3.0), 767.1428571)

    def test_power_avail_torque_limited2(self):
        """Test the right result for the torque limited case, with a varied max_driver_speed"""
        self.pump.limited = 'torque'
        self.pump.max_driver_speed = 4.0
        self.assertAlmostEqual(self.pump.power_available(3.0), 671.25)

    def test_power_avail_curve_limited(self):
        """Test the right result for the curve limited case"""
        self.pump.limited = 'curve'
        self.pump.driver = Driver("test driver", interpDict({0.5: 500.0,
                                                             0.6: 600.0,
                                                             0.75: 750.0,
                                                             0.85: 825.0,
                                                             0.95: 852.0,
                                                             1.00: 895.0,
                                                             }))
        self.pump.gear_ratio = 1/self.pump.design_speed
        self.assertAlmostEqual(self.pump.power_available(3.0), 826.9285714)

    def test_power_avail_none_limited(self):
        """Test the right result for the non-limited case"""
        self.pump.limited = None
        self.assertAlmostEqual(self.pump.power_available(3.0), 1915.670989 * (3/3.5)**3 * self.pump.slurry.rhom+1)


if __name__ == '__main__':
    unittest.main()
