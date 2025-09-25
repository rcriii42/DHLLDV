"""Test the LagrPipeline object"""

from DHLLDV.LagrPipe import LagrPipe, LagrPipeline
from DHLLDV.PipeObj import Pipe, Pipeline
from DHLLDV.SlurryObj import Slurry
from tests.test_Pipe import Ladder_Pump600, Main_Pump500

import unittest


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.pipe = Pipe(diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0)
        self.slurry = Slurry(fluid='salt')
        self.pipe_list = [Pipe('Entrance', 0.6, 0, 0.5, -4.0),
                          self.pipe,
                          Ladder_Pump600,
                          Pipe('MP Suction', 0.5, 25.0, 0.1, 0.0),
                          Main_Pump500,
                          Pipe('MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
                          Pipe('Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)]
        self.lpipeline = LagrPipeline(name="test lagrangian pipeline",
                                      pipe_list=[Pipe('Entrance', 0.6, 0, 0.5, -4.0),
                                                 self.pipe,
                                                 Ladder_Pump600,
                                                 Pipe('MP Suction', 0.5, 25.0, 0.1, 0.0),
                                                 Main_Pump500,
                                                 Pipe('MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
                                                 Pipe('Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)],
                                      slurry=self.slurry)

    def test_lpipeline_length(self):
        """Check the length of the slugs is the length of the pipeline"""
        slugs_length = 0
        for p in self.lpipeline.lpipe_list:
            if type(p) is LagrPipe:
                slugs_length += sum(s.length for s in p.slugs)
        self.assertEqual(self.lpipeline.total_length, slugs_length)

    def test_flow_matches_pipeline(self):
        """Check that the newly initiated lagrpipe flow matched the source pipeline operating point"""
        P = Pipeline('test_pipeline', self.pipe_list, self.slurry)
        flow_list = [P.pipesections[-1].flow(v) for v in P.slurry.vls_list]
        qop = P.find_operating_point(flow_list)
        q, h, slug = self.lpipeline.update()
        self.assertAlmostEqual(q, qop, places=4)

    def test_head_matches_pipeline(self):
        """Check that the newly initiated lagrpipe head matches the source pipeline operating point head"""
        P = Pipeline('test_pipeline', self.pipe_list, self.slurry)
        flow_list = [P.pipesections[-1].flow(v) for v in P.slurry.vls_list]
        qop = P.find_operating_point(flow_list)
        h_losses_slurry, h_losses_fluid, h_pump_fluid, h_pump_slurry = P.calc_system_head(qop)
        q, h_list, slug = self.lpipeline.update()

        self.assertAlmostEqual(sum(h_list), h_losses_slurry - h_pump_slurry, places=4)


if __name__ == '__main__':
    unittest.main()
