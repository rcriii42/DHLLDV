"""LagrSlug.py - The slug object for the LagrPumps"""

from copy import copy
from dataclasses import dataclass
from math import pi

from DHLLDV.SlurryObj import Slurry


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