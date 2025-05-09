import unittest

from DHLLDV.LagrPipe import add_slurries, LagrPipe, Slug
from DHLLDV.SlurryObj import Slurry


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.slurry1 = Slurry(Cv=0.2)
        self.slurry2 = Slurry(Cv=0.1)
        self.l_pipe = LagrPipe(slugs=[Slug(10.0, self.slurry1)])

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

    def test_add_slugs(self):
        new_slug = Slug(5.0, self.slurry1) + Slug(5.0, self.slurry2)
        self.assertEqual(new_slug.length, 10)
        self.assertEqual(new_slug.slurry.rhom, (self.slurry1.rhom + self.slurry2.rhom)/2)

    def test_init_lagrpipe(self):
        total_length = sum(s.length for s in self.l_pipe.slugs)
        self.assertAlmostEqual(10, total_length)

    def test_feed_rhom_out(self):
        self.l_pipe.feed_in = lambda q: (1.0, Slug(4.0, self.slurry2))
        h_out, slug_out = self.l_pipe.feed(1.824146925)
        self.assertEqual(slug_out.slurry.rhom, 1.34984824)
        self.assertAlmostEqual(slug_out.length, 4)

    def test_feed4_step_1(self):
        """Test the first step if velocity is 4 m/sec"""
        self.l_pipe.feed_in = lambda q: (1.0, Slug(4.0, self.slurry2))
        h_out, slurry_out = self.l_pipe.feed(1.824146925)
        total_length = sum(s.length for s in self.l_pipe.slugs)
        self.assertAlmostEqual(10, total_length)
        self.assertEqual(len(self.l_pipe.slugs), 2)
        self.assertEqual(self.l_pipe.slugs[0].slurry.rhom, self.slurry2.rhom)
        self.assertEqual(self.l_pipe.slugs[1].slurry.rhom, self.slurry1.rhom)
        self.assertAlmostEqual(h_out, 1 + 1.068679635)

    def test_feed4_step_2(self):
        """Test the second step if velocity is 4 m/sec"""
        self.l_pipe.feed_in = lambda q: (1.0, Slug(4.0, self.slurry2))
        for i in range(2):
            h_out, slug_out = self.l_pipe.feed(1.824146925)
        total_length = sum(s.length for s in self.l_pipe.slugs)
        self.assertAlmostEqual(10, total_length)
        self.assertEqual(len(self.l_pipe.slugs), 3)
        self.assertEqual(self.l_pipe.slugs[0].slurry.rhom, self.slurry2.rhom)
        self.assertEqual(self.l_pipe.slugs[1].slurry.rhom, self.slurry2.rhom)
        self.assertEqual(self.l_pipe.slugs[2].slurry.rhom, self.slurry1.rhom)
        self.assertAlmostEqual(h_out, 1 + 1.004257308)

    def test_feed5p5_step_2(self):
        """Test the second step if velocity is 5.5 m/sec"""
        self.l_pipe.feed_in = lambda q: (1.0, Slug(5.5, self.slurry2))
        for i in range(2):
            h_out, slug_out = self.l_pipe.feed(2.508202022)
        total_length = sum(s.length for s in self.l_pipe.slugs)
        self.assertAlmostEqual(10, total_length)
        self.assertEqual(len(self.l_pipe.slugs), 2)
        self.assertEqual(self.l_pipe.slugs[0].slurry.rhom, self.slurry2.rhom)
        self.assertEqual(self.l_pipe.slugs[1].slurry.rhom, self.slurry2.rhom)
        self.assertAlmostEqual(slug_out.slurry.rhom, 1.320299336)


if __name__ == '__main__':
    unittest.main()
