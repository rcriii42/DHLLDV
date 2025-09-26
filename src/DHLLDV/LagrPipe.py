"""LagrPipe.py - Pipe and Pipeline objects for the pumping simulation

Creates a Lagrangian view of the pipeline that tracks 'slugs' of slurry moving down the pipeline
"""

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from functools import partial
from math import pi

from DHLLDV.DHLLDV_constants import gravity
from DHLLDV.PumpObj import Pump
from DHLLDV.SlurryObj import Slurry
from DHLLDV.PipeObj import Pipe, Pipeline
from DHLLDV.LagrFeeds import FixedDensityFeed
from DHLLDV.LagrSlug import Slug


@dataclass
class LagrPipe(Pipe):
    """A Lagrangian view of the pipe that tracks 'slugs' of slurry moving through the pipe section """
    slugs: list[Slug] | None = None  # Length and Slurry of each slug
    feed_in: Callable[[float], (float, Slug)] | None = None  # The incoming feed function, see definition below

    def __post_init__(self):
        if self.slugs is None:
            self.slugs = [Slug(1.0, Slurry())]
        self.length = sum(s.length for s in self.slugs)

        # Check slugs are all the same diameter
        check_diameter = self.slugs[0].Dp
        for i, s in enumerate(self.slugs[0:]):
            if s.Dp != check_diameter:
                print(f'WARNING slug {i+1} in {self.name} diameter of {s.Dp:0.3f} does not match '
                      f'first slug {check_diameter=:0.3f}, setting to reference')
                s.Dp = check_diameter

    @classmethod
    def from_pipe(cls, this_pipe: Pipe,
                  feed_in: Callable[[float], (float, Slug)] | None = None,
                  slurry: Slurry | None = None) -> 'LagrPipe':
        """Create a LagrPipe from an existing Pipe"""
        if slurry is None:
            slurry = Slurry(Dp=this_pipe.diameter)
        else:
            slurry.Dp = this_pipe.diameter
        slugs = [Slug(length=this_pipe.length, slurry=deepcopy(slurry))]
        return cls(name=this_pipe.name,
                   diameter=this_pipe.diameter,
                   length=this_pipe.length,
                   total_K=this_pipe.total_K,
                   elev_change=this_pipe.elev_change,
                   slugs=slugs,
                   feed_in=feed_in
                   )

    @property
    def average_rhom(self):
        """Return the average density for all the slugs in this pipe"""
        if self.length > 0:
            return sum(s.rhom * s.length for s in self.slugs) / self.length
        else:
            return self.slugs[0].rhom

    @property
    def num_slugs(self):
        """Count the slugs in this pipe"""
        return len(self.slugs)

    def feed(self, Q: float) -> ([float, float, float], Slug):
        """
        Get slurry from upstream, update the slugs, and send slurry and head downstream

        Q is the quantity moved this timestep in m3

        Returns a tuple with a list of the total head to this point (Hvel, Hloss, Hpump), and the Slug passed downstream
        """
        h_in, in_slug = self.feed_in(Q)
        in_slug.Dp = self.diameter  # also updates the length to account for diameter changes
        vm = remain_length = self.velocity(Q)  # If the timestep is 1, the velocity is the slug length

        if self.length == 0:
            # For zero-length pipe sections just pass along the in_slug, keeping the slurry
            extruded_slug = in_slug
            self.slugs[0].slurry = deepcopy(in_slug.slurry)

        else:
            self.slugs.insert(0, in_slug)
            extruded_slug = Slug(0, deepcopy(self.slugs[-1].slurry))
            while remain_length > 0:
                last_slug = self.slugs[-1]
                if last_slug.length <= remain_length:
                    # Add the entire slug to the extruded slug
                    extruded_slug = extruded_slug + last_slug
                    remain_length -= last_slug.length
                    self.slugs = self.slugs[:-1]
                else:
                    # The last slug is too long, split it
                    new_slug = Slug(remain_length, deepcopy(last_slug.slurry))
                    extruded_slug = extruded_slug + new_slug
                    last_slug.length -= remain_length
                    remain_length = 0

        """Calculate the losses, does three things:
        
        Calculates friction and fitting losses and subtract from input losses
        Calculates the velocity head, adds change from previous pipe to losses
        Calculate the elevation head
        """
        hvel_in, hloss_in, hpump = h_in
        hvel_w = vm ** 2 / (2 * gravity)
        hvel_change = -1 * hvel_w * in_slug.rhom - hvel_in
        hloss_out = hloss_in + hvel_change
        for s in self.slugs:
            im = s.slurry.im(vm)  # Implicitly assume timestep is 1
            hloss_out -= im * s.length  # Friction losses
            if self.length > 0:
                hloss_out -= s.slurry.rhom * (self.total_K * s.length / self.length) * hvel_w  # Fitting losses
            else:
                hloss_out -= s.slurry.rhom * self.total_K * hvel_w  # Fitting losses

        if self.length > 0:
            for s in self.slugs:
                hloss_out -= s.slurry.rhom * s.length * self.elev_change / self.length  # elevation head requirement
        else:
            s = self.slugs[0]
            hloss_out -= s.rhom * self.elev_change  # elevation head requirement

        slugs_length = sum(s.length for s in self.slugs)
        if int(slugs_length * 1000) != int(self.length * 1000):
            diff = slugs_length - self.length
            print(f'WARNING {self.name=}: lengths do not add up {slugs_length=:0.3f} {self.length=:0.3f} '
                  f'{diff=:0.3e}')

        return [-1 * hvel_w * self.average_rhom, hloss_out, hpump], extruded_slug


class LagrPipeline(Pipeline):
    """Manage a Lagrangian pipeline that tracks slugs of slurry moving through a pipeline

    Has to:
    Connect the suction feed, LagrPipes and pumps
    Calculates acceleration/deceleration
    """

    def __init__(self, name="LagrPipeline", pipe_list=None, slurry=None, suct_feed=None):
        super().__init__(name, pipe_list, slurry)

        self.timecounter = 0  # Track the number of timesteps so far
        self.slurry.Dp = self.pipesections[-1].diameter
        self.lastflow = self.find_operating_point(self.slurry.vls_list)
        self.lpipe_list = []
        if suct_feed is not None:
            self.suction_feed = suct_feed
        else:
            self.suction_feed = FixedDensityFeed(deepcopy(self.slurry),
                                                 Dp=self.pipesections[0].diameter,
                                                 )
        last_feed = self.suction_feed.feed
        for i, element in enumerate(self.pipesections):
            if type(element) is Pipe:
                self.lpipe_list.append(LagrPipe.from_pipe(this_pipe=element, feed_in=last_feed, slurry=slurry))
                last_feed = self.lpipe_list[-1].feed
                if i > 0 and element.elev_change > element.length:
                    print(f'WARNING Pipe section {element.name} at position {i} length less than elevation change: '
                          f'{element.length=:0.3f} {element.elev_change=:0.3f}')

            elif type(element) is Pump:
                # add a feed method for the pump
                element.feed_in = last_feed

                def pump_feed(this_pump: Pump, Q: float) -> ([float, float, float], Slug):
                    """Function handle the feed of a pump object"""
                    h_in, in_slug = this_pump.feed_in(Q)
                    hvel_in, hloss_in, hpump_in = h_in
                    this_pump.slurry = in_slug.slurry
                    _, h, _, _ = this_pump.point(Q)
                    return [hvel_in, hloss_in, hpump_in + h], in_slug

                last_feed = partial(pump_feed, element)
                self.lpipe_list.append(element)

            else:
                print(f'LagrPipeline.__init__: Warning, unknown element type {type(element)} '
                      f'in pipeline at position {i}, not adding')

    @property
    def average_rhom(self):
        """Calculate the average density in the pipeline"""
        weight_sum = 0
        for p in self.lpipe_list:
            if type(p) is LagrPipe:
                weight_sum += p.length * p.average_rhom
        return weight_sum / self.total_length

    @property
    def num_slugs(self):
        return sum(p.num_slugs for p in self.lpipe_list if type(p) is LagrPipe)

    def update(self) -> tuple[float, [float, float, float], Slug]:
        """Update the pipeline by one second
        TODO: Allow user-input timestep?

        Advance time
        Call feed functions
        calculate acceleration/deceleration

        Returns the new flow, head tuple (velocity, losses, pump), and last slug"""
        self.timecounter += 1

        head_list, disch_slug = self.lpipe_list[-1].feed(self.lastflow)

        # net_head is the sum of the heads (losses and velocity head negative)
        # If net_head is negative, the system will decelerate
        hvel_out, hloss_out, hpump = head_list
        net_head = hloss_out + hpump
        pl_weight = 0
        for p in self.lpipe_list:
            if type(p) is LagrPipe:
                for s in p.slugs:
                    pl_weight += s.length * s.slurry.rhom
        acceleration = net_head / pl_weight
        # print(f'{net_head=:0.3f} {pl_weight=:0.3f} {acceleration=:0.3e}')
        # Use the last pump discharge diameter for acceleration calcs
        acc_pipe = self.lpipe_list[-1]
        vls = acc_pipe.velocity(self.lastflow)
        self.lastflow = acc_pipe.flow(vls + acceleration)

        return self.lastflow, [hvel_out, hloss_out, hpump], disch_slug


if __name__ == '__main__':
    from tests.test_Pipe import Ladder_Pump600, Main_Pump500

    slurry = Slurry(fluid='salt')
    pipe_list = [Pipe(name='Entrance', diameter=0.6, length=0, total_K=0.5, elev_change=-4.0),
                 Pipe(name='LP Suction', diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0),
                 Ladder_Pump600,
                 Pipe(name='MP Suction', diameter=0.5, length=25.0, total_K=0.1, elev_change=0.0),
                 Main_Pump500,
                 Pipe(name='MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
                 Pipe(name='Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)]
    lpipeline = LagrPipeline(name="test lagrangian pipeline",
                                  pipe_list=pipe_list,
                                  slurry=slurry)
    slugs_length = 0
    elev_change = 0
    for p in lpipeline.lpipe_list:
        if type(p) is LagrPipe:
            slugs_length += sum(s.length for s in p.slugs)
            elev_change += p.elev_change
    print(f'{lpipeline.total_length=:0.3f} {slugs_length=:0.3f} {elev_change=:0.3f}')

    P = Pipeline('test_pipeline', pipe_list, slurry)
    flow_list = [P.pipesections[-1].flow(v) for v in P.slurry.vls_list]
    qop = P.find_operating_point(flow_list)
    vop = P.pipesections[-1].velocity(qop)
    h_losses_slurry, h_losses_fluid, h_pump_fluid, h_pump_slurry = P.calc_system_head(qop)
    print(f'{qop=:0.3f} {vop=:0.3f} {h_losses_slurry=:0.3f}, {h_losses_fluid=:0.3f} {h_pump_slurry=:0.3f}, '
          f'{h_pump_fluid=:0.3f}')

    for i in range(5):
        q, h_list, extruded_slug = lpipeline.update()
        hvel_out, hloss_out, hpump = h_list
        hlosses = sum(h_list[:2])
        hvel_calc = extruded_slug.rhom * lpipeline.lpipe_list[-1].velocity(q)**2 / (2 * gravity)
        print(f'{lpipeline.timecounter=}, {q=:0.3f}, vls={lpipeline.lpipe_list[-1].velocity(q):0.3f}, '
              f'{hvel_calc=:0.3f}, {hvel_out=:0.3f}, {hloss_out=:0.3f} {hlosses=:0.3f}, {hpump=:0.3f}, '
              f'{extruded_slug.slurry.rhom=:0.3f}')
