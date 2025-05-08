"""LagrPipe.py - Pipe and Pipeline objects for the pumping simulation

Creates a Lagrangian view of the pipeline that tracks 'slugs' of slurry moving down the pipeline
"""

from collections.abc import Callable, Awaitable
from copy import copy
from dataclasses import dataclass
from math import pi
from types import FunctionType

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
class LagrPipe(Pipe):
    """A Lagrangian view of the pipe that tracks 'slugs' of slurry moving through the pipe section """
    slugs: list[(float, Slurry)] | None = None  # Length and Slurry of each slug
    feed_in: Callable[[float], tuple[float, Slurry]] | None = None  # Stub for the feed function

    def __post_init__(self):
        self.length = sum(s[0] for s in self.slugs)

    def feed(self, Q: float) -> (float, Slurry):
        """
        Get slurry from upstream, update the slugs, and send slurry and head downstream

        Q is the quantity moved this timestep in m3

        Returns a tuple of the total head requirement to date, and the Slurry passed downstream
        """
        in_h, in_slurry = self.feed_in(Q)
        in_slurry.Dp = self.slugs[0][1].Dp
        slug_length = self.velocity(Q)  # If the timestep is 1, the velocity is the slug length

        self.slugs.insert(0, (slug_length, in_slurry))

        extruded_len = 0
        extruded_slurry = None
        while extruded_len < slug_length:
            last_slug = self.slugs[-1]
            remain_len = slug_length - extruded_len
            if last_slug[0] <= remain_len:
                # Add the entire slug to the extruded slug
                extruded_slurry = add_slurries((extruded_slurry, extruded_len),
                                               (last_slug[1], last_slug[0]))
                extruded_len += last_slug[0]
                self.slugs = self.slugs[:-1]
            else:
                # The last slug is too long, split it
                extruded_slurry = add_slurries((extruded_slurry, extruded_len),
                                               (last_slug[1], remain_len))
                extruded_len += remain_len
                self.slugs[-1] = (last_slug[0] - remain_len, last_slug[1])

        for s in self.slugs:
            im = s[1].im(Q)  # Implicitly assume timestep is 1
            hvel = extruded_len**2 / (2 * gravity)
            in_h += im * s[0] + s[1].rhom * (self.total_K * s[0]/self.length) * hvel

        return in_h, extruded_slurry

