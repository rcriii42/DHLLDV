"""Test the LagrPipeline object"""

from DHLLDV.LagrPipe import LagrPipe, LagrPipeline
from DHLLDV.PipeObj import Pipe, Pipeline
from DHLLDV.SlurryObj import Slurry
from tests.test_Pipe import Ladder_Pump600, Main_Pump500

import unittest


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.slurry = Slurry(fluid='salt')
        self.pipe_list = [Pipe(name='Entrance', diameter=0.6, length=0, total_K=0.5, elev_change=-4.0),
                          Pipe(name='LP Suction', diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0),
                          Ladder_Pump600,
                          Pipe(name='MP Suction', diameter=0.5, length=25.0, total_K=0.1, elev_change=0.0),
                          Main_Pump500,
                          Pipe('MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
                          Pipe('Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)]
        self.lpipeline = LagrPipeline(name="test lagrangian pipeline",
                                      pipe_list=self.pipe_list,
                                      slurry=self.slurry)

    def test_lpipeline_length(self):
        """Check the length of the slugs is the length of the pipeline"""
        slugs_length = 0
        for p in self.lpipeline.lpipe_list:
            if type(p) is LagrPipe:
                slugs_length += sum(s.length for s in p.slugs)
        self.assertEqual(self.lpipeline.total_length, slugs_length)

    def test_lpipe_sender_length_on_dia_change(self):
        """Test that slugs lengths for the upstream pipe are correct when pipe diameter is changed"""
        q, h, slug = self.lpipeline.update()
        slugs_length = 0
        for s in self.lpipeline.lpipe_list[1].slugs:
            slugs_length += s.length
        self.assertEqual(slugs_length, self.lpipeline.lpipe_list[1].length)

    def test_lpipe_reciever_length_on_dia_change(self):
        """Test that slugs lengths for the downstream pipe are correct when pipe diameter is changed"""
        q, h, slug = self.lpipeline.update()
        slugs_length = 0
        for s in self.lpipeline.lpipe_list[3].slugs:
            slugs_length += s.length
        self.assertEqual(slugs_length, self.lpipeline.lpipe_list[3].length)

    def test_flow_matches_pipeline(self):
        """Check that the newly initiated lagrpipe flow matched the source pipeline operating point"""
        P = Pipeline('test_pipeline', self.pipe_list, self.slurry)
        flow_list = [P.pipesections[-1].flow(v) for v in P.slurry.vls_list]
        qop = P.find_operating_point(flow_list)
        q, h, slug = self.lpipeline.update()
        self.assertAlmostEqual(q, qop, places=4)

    def test_pump_head_matches_pipeline(self):
        """Check that the newly initiated lagrpipe head matches the source pipeline operating point head"""
        P = Pipeline('test_pipeline', self.pipe_list, self.slurry)
        flow_list = [P.pipesections[-1].flow(v) for v in P.slurry.vls_list]
        qop = P.find_operating_point(flow_list)
        h_losses_slurry, h_losses_fluid, h_pump_fluid, h_pump_slurry = P.calc_system_head(qop)
        q, h_list, slug = self.lpipeline.update()

        self.assertAlmostEqual(h_list[2], h_pump_slurry, places=4)

    def test_net_head_matches_pipeline(self):
        """Check that the newly initiated lagrpipe head matches the source pipeline operating point head"""
        P = Pipeline('test_pipeline', self.pipe_list, self.slurry)
        flow_list = [P.pipesections[-1].flow(v) for v in P.slurry.vls_list]
        qop = P.find_operating_point(flow_list)
        h_losses_slurry, h_losses_fluid, h_pump_fluid, h_pump_slurry = P.calc_system_head(qop)
        q, h_list, slug = self.lpipeline.update()

        self.assertAlmostEqual(sum(h_list[1:]), h_losses_slurry - h_pump_slurry, places=4)


if __name__ == '__main__':
    unittest.main()
