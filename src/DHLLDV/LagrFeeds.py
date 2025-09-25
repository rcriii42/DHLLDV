"""LagrFeeds.py - Various feed functions for the LagrPipeline"""

from copy import copy
from math import pi

from DHLLDV.LagrSlug import Slug
from DHLLDV.SlurryObj import Slurry


class FixedDensityFeed:
    """A class that has a simple feed mechanism to provide fixed-density feed to a project"""

    def __init__(self, slurry: Slurry, density: float = None, Dp: float = None):
        self.slurry = slurry
        if density is not None:
            self.slurry.rhom = density
        if Dp is not None:
            self.slurry.Dp = Dp

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

    # class CyclicFeed(FixedDensityFeed):