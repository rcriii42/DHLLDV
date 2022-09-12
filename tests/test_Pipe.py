"""Test the Pipe and Pipeline objects"""

import unittest

from DHLLDV.DHLLDV_Utils import interpDict
from DHLLDV.PipeObj import Pipe, Pipeline
from DHLLDV.PumpObj import Pump
from DHLLDV.stratified import areas

Ladder_Pump600 = Pump(name="0.600x0.600x1.118m Pump at 300 RPM",
                      design_speed=5.0,
                      design_impeller=1.1176,
                      suction_dia=0.6,
                      disch_dia=0.6,
                      design_QH_curve=interpDict({0.0000000: 21.430053,
                                                  0.1722065: 21.412179,
                                                  0.3444130: 21.327235,
                                                  0.5166194: 21.167398,
                                                  0.6888259: 20.928420,
                                                  0.8610324: 20.609779,
                                                  1.0332389: 20.214599,
                                                  1.2054454: 19.749335,
                                                  1.3776519: 19.223251,
                                                  1.5498583: 18.647749,
                                                  1.7220648: 18.035622,
                                                  1.8942713: 17.400307,
                                                  2.0664778: 16.755212,
                                                  2.2386843: 16.113174,
                                                  2.4108907: 15.486061,
                                                  2.5830972: 14.884552,
                                                  2.7553037: 14.318070,
                                                  3.0997167: 13.322144,
                                                  }),
                      design_QP_curve=interpDict({0.000000: 149.140000,
                                                  0.172206: 65.269284,
                                                  0.344413: 105.039933,
                                                  0.516619: 143.171017,
                                                  0.688826: 181.500777,
                                                  0.861032: 220.878834,
                                                  1.033239: 262.061262,
                                                  1.205445: 306.003106,
                                                  1.377652: 354.040500,
                                                  1.549858: 408.062625,
                                                  1.722065: 470.709112,
                                                  1.894271: 545.599628,
                                                  2.066478: 637.545159,
                                                  2.238684: 752.527526,
                                                  2.410891: 896.806727,
                                                  2.583097: 1073.607690,
                                                  2.755304: 1274.810680,
                                                  3.099717: 1589.740236,
                                                  }),
                      avail_power=550,
                      limited="torque",
                      )

Main_Pump500 = Pump(name="0.600x0.500x1.422m Pump at 450 RPM",
                    design_speed=7.50,
                    design_impeller=1.4224,
                    suction_dia=0.6,
                    disch_dia=0.5,
                    design_QH_curve=interpDict({0.0000000: 78.627157,
                                                0.1195878: 78.377502,
                                                0.2391757: 78.020587,
                                                0.3587635: 77.539928,
                                                0.4783513: 76.923729,
                                                0.5979392: 76.165052,
                                                0.7175270: 75.261842,
                                                0.8371148: 74.216805,
                                                0.9567027: 73.037111,
                                                1.0762905: 71.733957,
                                                1.1958783: 70.321994,
                                                1.3154662: 68.818664,
                                                1.4350540: 67.243488,
                                                1.5546418: 65.617353,
                                                1.6742297: 63.961839,
                                                1.7938175: 62.298616,
                                                1.9134054: 60.648952,
                                                2.1525810: 57.471239,
                                                }),
                    design_QP_curve=interpDict({0.000000: 596.560000,
                                                0.119588: 312.828525,
                                                0.239176: 452.214571,
                                                0.358764: 568.416766,
                                                0.478351: 671.536543,
                                                0.597939: 765.176468,
                                                0.717527: 851.008969,
                                                0.837115: 929.976294,
                                                0.956703: 1002.741242,
                                                1.076291: 1069.890871,
                                                1.195878: 1132.036558,
                                                1.315466: 1189.862444,
                                                1.435054: 1244.145028,
                                                1.554642: 1295.755647,
                                                1.674230: 1345.652771,
                                                1.793818: 1394.868582,
                                                1.913405: 1444.492652,
                                                2.152581: 1549.504172,
                                                }),
                    avail_power=1800,
                    limited="torque",
                    )


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.pipe = Pipe(diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0)
        self.pipeline = Pipeline(name="test pipeline",
                                 pipe_list=[Pipe('Entrance', 0.6, 0, 0.5, -4.0),
                                            self.pipe,
                                            Ladder_Pump600,
                                            Pipe('MP Suction', 0.5, 25.0, 0.1, 0.0),
                                            Main_Pump500,
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
        self.assertAlmostEqual(self.pipeline.total_power, 2350)

    def test_slurries_updated(self):
        self.pipeline.Cv = 0.1
        for p in self.pipeline.pipesections:
            if isinstance(p, Pump):
                with self.subTest(msg=f'Test slurry changed for {p.name}'):
                    self.assertAlmostEqual(p.slurry.Cv, 0.1)
            else:
                with self.subTest(msg=f'Test slurry exists for {p.diameter:0.3f} pipe'):
                    self.assertAlmostEqual(self.pipeline.slurries[p.diameter].Cv, 0.1)

    def test_total_head_slurry(self):
        """Test the total head calc on slurry"""
        Hpipe_m, Hpipe_l, Hpump_l, Hpump_m = self.pipeline.calc_system_head(1.55425794)
        self.assertAlmostEqual(Hpipe_m, 110.327, places=2)

    def test_total_head_fluid(self):
        """Test the total head calc on fluid"""
        Hpipe_m, Hpipe_l, Hpump_l, Hpump_m = self.pipeline.calc_system_head(1.55425794)
        self.assertAlmostEqual(Hpipe_l, 92.036, places=2)

    def test_friction_head_slurry(self):
        """Test the pipeline on slurry without elevation or fitting losses"""
        for p in self.pipeline.pipesections:
            if isinstance(p, Pipe):
                p.total_K = 0
                p.elev_change = 0
        Hpipe_m, Hpipe_l, Hpump_l, Hpump_m = self.pipeline.calc_system_head(1.55425794)
        self.assertAlmostEqual(Hpipe_m, 101.24533, places=1)

    def test_head_no_elev_slurry(self):
        """Test the pipeline on slurry without elevation changes"""
        for p in self.pipeline.pipesections:
            if isinstance(p, Pipe):
                p.elev_change = 0
        Hpipe_m, Hpipe_l, Hpump_l, Hpump_m = self.pipeline.calc_system_head(1.55425794)
        self.assertAlmostEqual(Hpipe_m, 107.8803, places=1)

    def test_friction_head_fluid(self):
        """Test the pipeline on fluid without elevation or fitting losses"""
        for p in self.pipeline.pipesections:
            if isinstance(p, Pipe):
                p.total_K = 0
                p.elev_change = 0
        Hpipe_m, Hpipe_l, Hpump_l, Hpump_m = self.pipeline.calc_system_head(1.55425794)
        self.assertAlmostEqual(Hpipe_l, 85.81389, places=1)

    def test_total_head_no_elev_fluid(self):
        """Test the pipeline on fluid without elevation changes"""
        for p in self.pipeline.pipesections:
            if isinstance(p, Pipe):
                p.elev_change = 0
        Hpipe_m, Hpipe_l, Hpump_l, Hpump_m = self.pipeline.calc_system_head(1.55425794)
        self.assertAlmostEqual(Hpipe_l, 91.0108, places=1)

    def test_qimin(self):
        """Test the qimin calculation"""
        flow_list = [self.pipeline.pipesections[-1].flow(v) for v in self.pipeline.slurry.vls_list]
        qimin = self.pipeline.qimin(flow_list, precision=0.01)
        self.assertAlmostEqual(qimin, 1.11919235, places=1)

    def test_intersection(self):
        """Test the operating point calculation"""
        flow_list = [self.pipeline.pipesections[-1].flow(v) for v in self.pipeline.slurry.vls_list]
        qop = self.pipeline.find_operating_point(flow_list)
        self.assertAlmostEqual(qop, 1.55425794, places=3)


if __name__ == '__main__':
    unittest.main()