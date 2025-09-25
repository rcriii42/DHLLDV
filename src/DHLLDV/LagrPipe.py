"""LagrPipe.py - Pipe and Pipeline objects for the pumping simulation

Creates a Lagrangian view of the pipeline that tracks 'slugs' of slurry moving down the pipeline
"""

from collections.abc import Callable
from copy import copy
from dataclasses import dataclass
from functools import partial
from math import pi

from DHLLDV.DHLLDV_constants import gravity
from DHLLDV.PumpObj import Pump
from DHLLDV.SlurryObj import Slurry
from DHLLDV.PipeObj import Pipe, Pipeline


def add_slurries(sw1: [Slurry | None, float], sw2: [Slurry | None, float]) -> Slurry:
    """Create a weighted average of two slurries

    Returns a new Slurry with averaged density, eventually needs to combine the GSDs, etc"""
    if sw1[0] is None:
        return sw2[0]
    elif sw2[0] is None:
        return sw1[0]
    rho_new = (sw1[0].rhom * sw1[1] + sw2[0].rhom * sw2[1])/(sw1[1] + sw2[1])
    new_slurry = copy(sw2[0])
    new_slurry.rhom = rho_new
    return new_slurry


@dataclass
class Slug:
    """A slug of slurry in the pipeline"""
    length: float
    slurry: Slurry

    def __add__(self, other):
        """Add two slugs together"""
        if type(other) is Slug:
            return Slug(self.length + other.length,
                        add_slurries((self.slurry, self.length), (other.slurry, other.length)))
        else:
            raise TypeError

    @property
    def rhom(self):
        """The density of the slurry"""
        return self.slurry.rhom

    @property
    def Dp(self):
        """The pipe diameter"""
        return self.slurry.Dp

    @Dp.setter
    def Dp(self, value):
        """Update the slug length when the Dp changes"""
        orig_q = self.length * self.area
        self.slurry.Dp = value
        self.length = orig_q / self.area

    @property
    def area(self):
        """THe area of the slug pipe"""
        return pi * (self.Dp / 2) ** 2


class FixedDensityFeed:
    """A class that has a simple feed mechanism to provide fixed-density feed to a project"""

    def __init__(self, slurry: Slurry, density: float = None, Dp: float = None, elevation_change: float = 0):
        self.slurry = slurry
        if density is not None:
            self.slurry.rhom = density
        if Dp is not None:
            self.slurry.Dp = Dp
        self.elevation_change = elevation_change

    @property
    def rhom(self):
        """"The feed density"""
        return self.slurry.rhom

    @rhom.setter
    def rhom(self, value):
        self.slurry.rhom = value

    @property
    def Dp(self):
        """The suction diameter (m)"""
        return self.slurry.Dp

    @Dp.setter
    def Dp(self, value):
        self.slurry.Dp = value

    @property
    def area(self):
        """THe area of the suction pipe"""
        return pi * (self.Dp/2)**2

    def feed(self, Q: float) -> ([float, float, float], Slug):
        """Return head of 0, and a slug of slurry

        The head is all calculated in the pipe sections"""
        Vls = Q/self.area

        return [0.0, 0.0, 0.0], Slug(Vls, copy(self.slurry))


@dataclass
class LagrPipe(Pipe):
    """A Lagrangian view of the pipe that tracks 'slugs' of slurry moving through the pipe section """
    slugs: list[Slug] | None = None  # Length and Slurry of each slug
    feed_in: Callable[[float], (float, Slug)] | None = None  # The incoming feed function, see definition below

    def __post_init__(self):
        self.length = sum(s.length for s in self.slugs)

    @classmethod
    def from_pipe(cls, this_pipe: Pipe,
                  feed_in: Callable[[float], (float, Slug)] | None = None,
                  slurry: Slurry | None = None) -> 'LagrPipe':
        """Create a LagrPipe from an existing Pipe"""
        if slurry is None:
            slurry = Slurry(Dp=this_pipe.diameter)
        slugs = [Slug(length=this_pipe.length, slurry=copy(slurry))]
        return cls(name=this_pipe.name,
                   diameter=this_pipe.diameter,
                   length=this_pipe.length,
                   total_K=this_pipe.total_K,
                   elev_change=this_pipe.elev_change,
                   slugs=slugs,
                   feed_in=feed_in
                   )

    def average_rhom(self):
        """Return the average density for all the slugs in this pipe"""
        if self.length > 0:
            return sum(s.rhom * s.length for s in self.slugs) / self.length
        else:
            return self.slugs[0].rhom

    def feed(self, Q: float) -> ([float, float, float], Slug):
        """
        Get slurry from upstream, update the slugs, and send slurry and head downstream

        Q is the quantity moved this timestep in m3

        Returns a tuple with a list of the total head to this point (Hvel, Hloss, Hpump), and the Slug passed downstream
        """
        h_in, in_slug = self.feed_in(Q)
        in_slug.Dp = self.slugs[0].slurry.Dp  # also updates the length to account for diameter changes
        vm = remain_length = self.velocity(Q)  # If the timestep is 1, the velocity is the slug length

        if self.length == 0:
            # For zero-length pipe sections just pass along the in_slug, keeping the slurry
            extruded_slug = in_slug
            self.slugs[0].slurry = copy(in_slug.slurry)

        else:
            self.slugs.insert(0, in_slug)
            extruded_slug = Slug(0, copy(self.slugs[-1].slurry))
            while remain_length > 0:
                last_slug = self.slugs[-1]
                if last_slug.length <= remain_length:
                    # Add the entire slug to the extruded slug
                    extruded_slug = extruded_slug + last_slug
                    remain_length -= last_slug.length
                    self.slugs = self.slugs[:-1]
                else:
                    # The last slug is too long, split it
                    new_slug = Slug(remain_length, copy(last_slug.slurry))
                    extruded_slug = extruded_slug + new_slug
                    last_slug.length -= remain_length
                    remain_length = 0

        """Calculate the losses, does three things:
        
        Calculates friction and fitting losses and subtract from input losses
        Calculates the velocity head
        Calculate the elevation head
        """
        hvel_in, hloss_in, hpump = h_in
        hvel_w = vm ** 2 / (2 * gravity)
        hloss_out = hloss_in
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
            print(f'WARNING {self.name=}: lengths do not add up {slugs_length=:0.3f} {self.length=:0.3f}')

        return [-1 * hvel_w * self.average_rhom(), hloss_out, hpump], extruded_slug


class LagrPipeline(Pipeline):
    """Manage a Lagrangian pipeline that tracks slugs of slurry moving through a pipeline

    Has to:
    Connect the suction feed, LagrPipes and pumps
    Calculates acceleration/deceleration
    """

    def __init__(self, name="LagrPipeline", pipe_list=None, slurry=None):
        super().__init__(name, pipe_list, slurry)

        self.timecounter = 0  # Track the number of timesteps so far
        self.slurry.Dp = self.pipesections[-1].diameter
        self.lastflow = self.find_operating_point(self.slurry.vls_list)
        self.lpipe_list = []
        self.suction_feed = FixedDensityFeed(copy(self.slurry),
                                             Dp=self.pipesections[0].diameter,
                                             elevation_change=self.pipesections[0].elev_change)
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
        _, hloss_out, hpump = head_list
        hvel_out = -1 * disch_slug.rhom * self.lpipe_list[-1].velocity(self.lastflow)**2 / (2 * gravity)
        net_head = hvel_out + hloss_out + hpump
        pl_weight = 0
        for p in self.lpipe_list:
            if type(p) is LagrPipe:
                for s in p.slugs:
                    pl_weight += s.length * s.slurry.rhom
        acceleration = net_head / pl_weight
        # Use the last pump discharge diameter for acceleration calcs
        acc_pipe = self.lpipe_list[-1]
        vls = acc_pipe.velocity(self.lastflow)
        self.lastflow = acc_pipe.flow(vls + acceleration)

        return self.lastflow, [hvel_out, hloss_out, hpump], disch_slug


if __name__ == '__main__':
    from tests.test_Pipe import Ladder_Pump600, Main_Pump500

    slurry = Slurry(fluid='salt')
    pipe_list = [Pipe('Entrance', 0.6, 0, 0.5, -4.0),
                 Pipe(name='LP Suction', diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0),
                 Ladder_Pump600,
                 Pipe('MP Suction', 0.5, 25.0, 0.1, 0.0),
                 Main_Pump500,
                 Pipe('MP Discharge', diameter=0.5, length=20.0, total_K=0.2,
                      elev_change=-1.0),
                 Pipe('Discharge', diameter=0.5, length=1000.0, total_K=1.0,
                      elev_change=1.0)]
    lpipeline = LagrPipeline(name="test lagrangian pipeline",
                                  pipe_list=pipe_list,
                                  slurry=slurry)
    slugs_length = 0
    elev_change = 0
    for p in lpipeline.lpipe_list:
        if type(p) is LagrPipe:
            slugs_length += sum(s.length for s in p.slugs)
            elev_change += p.elev_change
    print(f'{slugs_length=:0.3f} {elev_change=:0.3f}')

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
        print(f'{lpipeline.timecounter=}, {q=:0.3f}, vls={lpipeline.pipesections[-1].velocity(q):0.3f}, '
              f'{hvel_out=:0.3f}, {hloss_out=:0.3f} {hlosses=:0.3f}, {hpump=:0.3f}, '
              f'{extruded_slug.slurry.rhom=:0.3f}')
