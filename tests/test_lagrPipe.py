import unittest

from DHLLDV.LagrPipe import add_slurries, LagrPipe
from DHLLDV.SlurryObj import Slurry


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.slurry1 = Slurry(Cv=0.2)
        self.slurry2 = Slurry(Cv=0.1)
        self.l_pipe = LagrPipe(slugs=[(10.0, self.slurry1)])

    def test_add_slurries_first_none(self):
        new_slurry = add_slurries((None, 1), (self.slurry2, 1))
        self.assertEqual(new_slurry.rhom, self.slurry2.rhom)

    def test_add_slurries_second_none(self):
        new_slurry = add_slurries((self.slurry1, 1), (None, 1))
        self.assertEqual(new_slurry.rhom, self.slurry1.rhom)

    def test_add_slurries_equal_weight(self):
        new_slurry = add_slurries((self.slurry1, 1), (self.slurry2, 1))
        rho_expect = (self.slurry1.rhom + self.slurry2.rhom)/2
        self.assertEqual(new_slurry.rhom, rho_expect)

    def test_add_slurries_unequal_weight(self):
        new_slurry = add_slurries((self.slurry1, 0.75), (self.slurry2, 0.33))
        rho_expect = (self.slurry1.rhom*0.75 + self.slurry2.rhom*0.33)/(0.75+0.33)
        self.assertEqual(new_slurry.rhom, rho_expect)

    def test_init_lagrpipe(self):
        total_length = sum(s[0] for s in self.l_pipe.slugs)
        self.assertEqual(10, total_length)

    def test_feed_rhom_out(self):
        self.l_pipe.feed_in = lambda q: (1.0, self.slurry2)
        h_out, slurry_out = self.l_pipe.feed(1.824146925)
        self.assertEqual(slurry_out.rhom, 1.34984824)

    def test_feed5_step_1(self):
        """Test the first step if velocity is 5 m/sec"""
        self.l_pipe.feed_in = lambda q: (1.0, self.slurry2)
        h_out, slurry_out = self.l_pipe.feed(1.824146925)
        total_length = sum(s[0] for s in self.l_pipe.slugs)
        self.assertEqual(10, total_length)
        self.assertEqual(len(self.l_pipe.slugs), 2)
        self.assertEqual(self.l_pipe.slugs[0][1].rhom, self.slurry2.rhom)
        self.assertEqual(self.l_pipe.slugs[1][1].rhom, self.slurry1.rhom)
        self.assertEqual(h_out, 1 + 0.744833687)

    def test_feed5_step_2(self):
        """Test the second step if velocity is 5 m/sec"""
        self.l_pipe.feed_in = lambda q: (1.0, self.slurry2)
        h_out, slurry_out = self.l_pipe.feed(1.824146925)
        h_out, slurry_out = self.l_pipe.feed(1.824146925)
        total_length = sum(s[0] for s in self.l_pipe.slugs)
        self.assertEqual(10, total_length)
        self.assertEqual(len(self.l_pipe.slugs), 3)
        self.assertEqual(self.l_pipe.slugs[0][1].rhom, self.slurry2.rhom)
        self.assertEqual(self.l_pipe.slugs[1][1].rhom, self.slurry2.rhom)
        self.assertEqual(self.l_pipe.slugs[2][1].rhom, self.slurry1.rhom)

    def test_feed5p5_step_2(self):
        """Test the second step if velocity is 5.5 m/sec"""
        self.l_pipe.feed_in = lambda q: (1.0, self.slurry2)
        for i in range(2):
            h_out, slurry_out = self.l_pipe.feed(2.508202022)
        total_length = sum(s[0] for s in self.l_pipe.slugs)
        self.assertEqual(10, total_length)
        self.assertEqual(len(self.l_pipe.slugs), 2)
        self.assertEqual(self.l_pipe.slugs[0][1].rhom, self.slurry2.rhom)
        self.assertEqual(self.l_pipe.slugs[1][1].rhom, self.slurry2.rhom)
        self.assertAlmostEqual(slurry_out.rhom, 1.320299336)


if __name__ == '__main__':
    unittest.main()
