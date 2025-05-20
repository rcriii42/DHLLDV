"""Test the LagrPipeline object"""

from DHLLDV.LagrPipe import LagrPipe, LagrPipeline
from DHLLDV.PipeObj import Pipe, Pipeline
from DHLLDV.SlurryObj import Slurry
from tests.test_Pipe import Ladder_Pump600, Main_Pump500

import unittest


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.pipe = Pipe(diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0)
        slurry = Slurry(fluid='salt')
        self.lpipeline = LagrPipeline(name="test lagrangian pipeline",
                                      pipe_list=[Pipe('Entrance', 0.6, 0, 0.5, -4.0),
                                                 self.pipe,
                                                 Ladder_Pump600,
                                                 Pipe('MP Suction', 0.5, 25.0, 0.1, 0.0),
                                                 Main_Pump500,
                                                 Pipe('MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
                                                 Pipe('Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)],
                                      slurry=slurry)

    def test_lpipeline_length(self):
        """Check the length of the slugs is the length of the pipeline"""
        slugs_length = 0
        for p in self.lpipeline.lpipe_list:
            if type(p) is LagrPipe:
                slugs_length += sum(s.length for s in p.slugs)
        self.assertEqual(self.lpipeline.total_length, slugs_length)


if __name__ == '__main__':
    unittest.main()
