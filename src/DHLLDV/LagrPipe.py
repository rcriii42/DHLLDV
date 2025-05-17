"""LagrPipe.py - Pipe and Pipeline objects for the pumping simulation

Creates a Lagrangian view of the pipeline that tracks 'slugs' of slurry moving down the pipeline
"""

from collections.abc import Callable
from copy import copy
from dataclasses import dataclass
from math import pi

import scipy.optimize
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


class SuctionFeed():
    """A class that has a simple feed mechanism to provide fixed-density feed to a project"""

    def __init__(self, slurry: Slurry, density: float = None, Dp: float = None, suct_elev: float = 0):
        self.slurry = slurry
        if density is not None:
            self.slurry.rhom = density
        if Dp is not None:
            self.slurry.Dp = Dp
        self.elev = suct_elev

    @property
    def rhom(self):
        return self.slurry.rhom

    @rhom.setter
    def rhom(self, value):
        self.slurry.rhom = value

    @property
    def Dp(self):
        return self.slurry.Dp

    @Dp.setter
    def Dp(self, value):
        self.slurry.Dp = value

    @property
    def area(self):
        """THe area of the suction pipe"""
        return pi * (self.Dp/2)**2

    def feed(self, Q: float) -> (float, Slug):
        """Return the suction elevation head and a slug of slurry"""
        return self.slurry.rhom * self.elev, Slug(Q/self.area, self.slurry)

@dataclass
class LagrPipe(Pipe):
    """A Lagrangian view of the pipe that tracks 'slugs' of slurry moving through the pipe section """
    slugs: list[Slug] | None = None  # Length and Slurry of each slug
    feed_in: Callable[[float], (float, Slug)] | None = None  # The incoming feed function, see definition below

    def __post_init__(self):
        self.length = sum(s.length for s in self.slugs)

    def feed(self, Q: float) -> (float, Slug):
        """
        Get slurry from upstream, update the slugs, and send slurry and head downstream

        Q is the quantity moved this timestep in m3

        Returns a tuple of the total head requirement to date, and the Slug passed downstream
        """
        h_in, in_slug = self.feed_in(Q)
        in_slug.slurry.Dp = self.slugs[0].slurry.Dp
        vm = remain_length = self.velocity(Q)  # If the timestep is 1, the velocity is the slug length

        self.slugs.insert(0, in_slug)

        extruded_slug = Slug(0, copy(self.slugs[-1].slurry))
        while remain_length > 0:
            last_slug = self.slugs[-1]
            if last_slug.length <= remain_length:
                # Add the entire slug to the extruded slug
                extruded_slug += last_slug
                remain_length -= last_slug.length
                self.slugs = self.slugs[:-1]
            else:
                # The last slug is too long, split it
                new_slug = Slug(remain_length, copy(last_slug.slurry))
                extruded_slug += new_slug
                last_slug.length -= remain_length
                remain_length = 0

        for s in self.slugs:
            im = s.slurry.im(vm)  # Implicitly assume timestep is 1
            hvel = vm**2 / (2 * gravity)
            h_in += im * s.length + s.slurry.rhom * (self.total_K * s.length/self.length) * hvel

        return h_in, extruded_slug
