"""Test the Pipe and Pipeline objects"""

import unittest

from DHLLDV.DHLLDV_Utils import interpDict
from DHLLDV.PipeObj import Pipe, Pipeline
from DHLLDV.PumpObj import Pump
from DHLLDV.stratified import areas

Ladder_Pump = Pump(name="0.864x0.864x1.880m Pump at 225 RPM",
                   design_speed=3.75,
                   design_impeller=1.88,
                   suction_dia=0.864,
                   disch_dia=0.864,
                   design_QH_curve=interpDict({0.0000000: 34.161388,
                                               0.3567568: 34.109928,
                                               0.7135136: 33.968864,
                                               1.0702704: 33.727283,
                                               1.4270272: 33.378805,
                                               1.7837840: 32.921761,
                                               2.1405408: 32.359135,
                                               2.4972976: 31.698232,
                                               2.8540544: 30.950121,
                                               3.2108112: 30.128877,
                                               3.5675680: 29.250727,
                                               3.9243248: 28.333156,
                                               4.2810816: 27.394067,
                                               4.6378384: 26.451062,
                                               4.9945952: 25.520877,
                                               5.3513520: 24.619007,
                                               5.7081088: 23.759512,
                                               6.4216224: 22.216815,
                                               }),
                   design_QP_curve=interpDict({0.000000: 149.140000,
                                               0.356757: 265.086004,
                                               0.713514: 407.005162,
                                               1.070270: 534.014231,
                                               1.427027: 653.694156,
                                               1.783784: 768.682260,
                                               2.140541: 880.423455,
                                               2.497298: 990.182072,
                                               2.854054: 1099.454369,
                                               3.210811: 1210.185521,
                                               3.567568: 1324.910404,
                                               3.924325: 1446.866948,
                                               4.281082: 1580.106542,
                                               4.637838: 1729.610908,
                                               4.994595: 1901.405500,
                                               5.351352: 2102.626065,
                                               5.708109: 2341.436276,
                                               6.421622: 2966.399621,
                                               }),
                   avail_power=1491.4,
                   limited="torque",
                   )

Main_Pump = Pump(name="0.864x0.864x2.134m Pump at 315 RPM",
                 design_speed=5.25,
                 design_impeller=2.134,
                 suction_dia=0.864,
                 disch_dia=0.864,
                 design_QH_curve=interpDict({0.0000000: 86.747272,
                                            0.3567568: 86.450473,
                                            0.7135136: 86.051460,
                                            1.0702704: 85.533415,
                                            1.4270272: 84.883885,
                                            1.7837840: 84.094935,
                                            2.1405408: 83.163187,
                                            2.4972976: 82.089738,
                                            2.8540544: 80.879942,
                                            3.2108112: 79.543051,
                                            3.5675680: 78.091749,
                                            3.9243248: 76.541591,
                                            4.2810816: 74.910387,
                                            4.6378384: 73.217564,
                                            4.9945952: 71.483541,
                                            5.3513520: 69.729161,
                                            5.7081088: 67.975189,
                                            6.4216224: 64.548811,
                                            }),
                 design_QP_curve=interpDict({0.000000: 596.560000,
                                            0.356757: 921.629130,
                                            0.713514: 1349.538023,
                                            1.070270: 1712.125463,
                                            1.427027: 2039.315319,
                                            1.783784: 2341.820028,
                                            2.140541: 2624.644708,
                                            2.497298: 2890.613974,
                                            2.854054: 3141.699072,
                                            3.210811: 3379.626591,
                                            3.567568: 3606.189582,
                                            3.924325: 3823.412498,
                                            4.281082: 4033.634912,
                                            4.637838: 4239.546513,
                                            4.994595: 4444.191894,
                                            5.351352: 4650.956491,
                                            5.708109: 4863.540484,
                                            6.421622: 5322.321057,
                                            }),
                 avail_power=4239.3,
                 limited="torque",
                 )


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.pipe = Pipe(diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0)
        self.pipeline = Pipeline([Pipe('Entrance', 0.6, 0, 0.5, -4.0),
                                  self.pipe,
                                  Ladder_Pump,
                                  Pipe('MP Suction', 0.5, 25.0, 0.1, 0.0),
                                  Main_Pump,
                                  Pipe('MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
                                  Pipe('Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)])
        self.pipeline.slurry.fluid = 'salt'
        self.pipeline.update_slurries()

    def test_v(self):
        """Test Pipe.velocity"""
        self.assertAlmostEqual(self.pipe.velocity(1.0), 1.0/areas(0.6, 0.0)[0])

    def test_Q(self):
        """Test Pipe.flow"""
        self.assertAlmostEqual(self.pipe.flow(1.0), areas(0.6, 0.0)[0])

    def test_total_length(self):
        self.assertEqual(self.pipeline.total_length, 1055.0)

    def test_numsections(self):
        self.assertEqual(self.pipeline.num_pipesections, 5)

    def test_total_k(self):
        self.assertAlmostEqual(self.pipeline.total_K, 1.9)

    def test_total_lift(self):
        self.assertAlmostEqual(self.pipeline.total_lift, 1.0)

    def test_num_pumps(self):
        self.assertEqual(self.pipeline.num_pumps, 2)

    def test_total_power(self):
        self.assertAlmostEqual(self.pipeline.total_power, 5730.7)

    def test_slurries_updated(self):
        self.pipeline.Cv = 0.1
        for p in self.pipeline.pipesections:
            if isinstance(p, Pump):
                with self.subTest(msg=f'Test slurry changed for {p.name}'):
                    self.assertAlmostEqual(p.slurry.Cv, 0.1)
            else:
                with self.subTest(msg=f'Test slurry exists for {p.diameter:0.3f} pipe'):
                    self.assertAlmostEqual(self.pipeline.slurries[p.diameter].Cv, 0.1)

    # def test_total_head_slurry(self):
    #     """Test the total head calc on slurry"""
    #     Hpipe_m, Hpipe_l, Hpump_l, Hpump_m = self.pipeline.calc_system_head(1.215796)
    #     self.assertAlmostEqual(Hpipe_m, 96.50397004)
    #
    # def test_total_head_fluid(self):
    #     """Test the total head calc on fluid"""
    #     Hpipe_m, Hpipe_l, Hpump_l, Hpump_m = self.pipeline.calc_system_head(1.215796)
    #     self.assertAlmostEqual(Hpipe_l, 25.76477185)
    #
    def test_friction_head_slurry(self):
        """Test the pipeline on slurry without elevation or fitting losses"""
        for p in self.pipeline.pipesections:
            if isinstance(p, Pipe):
                p.total_K = 0
                p.elev_change = 0
        Hpipe_m, Hpipe_l, Hpump_l, Hpump_m = self.pipeline.calc_system_head(1.21579636)
        self.assertAlmostEqual(Hpipe_m, 82.23280988, places=4)

    # def test_friction_head_fluid(self):
    #     """Test the pipeline on fluid without elevation or fitting losses"""
    #     for p in self.pipeline.pipesections:
    #         if isinstance(p, Pipe):
    #             p.total_K = 0
    #             p.elev_change = 0
    #     Hpipe_m, Hpipe_l, Hpump_l, Hpump_m = self.pipeline.calc_system_head(1.215796)
    #     self.assertAlmostEqual(Hpipe_l, 21.5570364, places=1)

if __name__ == '__main__':
    unittest.main()