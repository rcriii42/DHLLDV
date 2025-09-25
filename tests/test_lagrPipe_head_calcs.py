"""Test the headloss calculations of the LagrPipe"""
import unittest

from DHLLDV.DHLLDV_constants import gravity
from DHLLDV.LagrPipe import LagrPipe, Slug, FixedDensityFeed
from DHLLDV.PipeObj import Pipe
from DHLLDV.SlurryObj import Slurry


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.slurry = Slurry(Cv=0.2)
        self.suct_feed = FixedDensityFeed(self.slurry)
        self.l_pipe = LagrPipe(slugs=[Slug(10.0, self.slurry)],
                               feed_in=self.suct_feed.feed)
        self.pipe = Pipe(diameter=self.slurry.Dp, length=10.0)

    def test_velocity_head(self):
        q = 1.82
        heads, out_slug = self.l_pipe.feed(q)
        hvel, hloss, hpump = heads
        self.assertAlmostEqual(hvel,
                               -1 * self.slurry.rhom * self.pipe.velocity(q)**2 / (2 * gravity)
                               )

    def test_pump_head(self):
        q = 1.82
        heads, out_slug = self.l_pipe.feed(q)
        hvel, hloss, hpump = heads
        self.assertAlmostEqual(hpump, 0.0)

    def test_head_losses(self):
        q = 1.82
        heads, out_slug = self.l_pipe.feed(q)
        hvel, hloss, hpump = heads
        fric_loss = -1 * self.slurry.im(self.pipe.velocity(q)) * self.pipe.length
        vel_head = -1 * self.slurry.rhom * self.pipe.velocity(q)**2 / (2 * gravity)
        self.assertAlmostEqual(hloss,
                               fric_loss + vel_head
                               )

    def test_head_losses_with_elev(self):
        q = 1.82
        elev_change = 1
        self.l_pipe.elev_change = self.pipe.elev_change = elev_change
        heads, out_slug = self.l_pipe.feed(q)
        hvel, hloss, hpump = heads
        fric_loss = -1 * self.slurry.im(self.pipe.velocity(q)) * self.pipe.length
        vel_head = -1 * self.slurry.rhom * self.pipe.velocity(q) ** 2 / (2 * gravity)
        elev_loss = -1 * elev_change * self.slurry.rhom
        self.assertAlmostEqual(hloss,
                               fric_loss + vel_head + elev_loss,
                               )

    def test_head_losses_with_K(self):
        q = 1.82
        k = 0.5
        self.l_pipe.total_K = self.pipe.total_K = k
        heads, out_slug = self.l_pipe.feed(q)
        hvel, hloss, hpump = heads
        fric_loss = -1 * self.slurry.im(self.pipe.velocity(q)) * self.pipe.length
        vel_head = -1 * self.slurry.rhom * self.pipe.velocity(q) ** 2 / (2 * gravity)
        fitting_loss = -1 * k * self.slurry.rhom * self.pipe.velocity(q)**2 / (2 * gravity)
        self.assertAlmostEqual(hloss,
                               fric_loss + vel_head + fitting_loss,
                               )


if __name__ == '__main__':
    unittest.main()
