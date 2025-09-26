"""LagrFeeds.py - Various feed functions for the LagrPipeline"""

from copy import deepcopy
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

        return [0.0, 0.0, 0.0], Slug(Vls, deepcopy(self.slurry))

class CyclicFeed(FixedDensityFeed):
    """A feed function with a simple varying density list"""

    def __init__(self, slurry: Slurry, densities: list[float] | None = None, Dp: float = None):
        self.slurry = slurry
        if densities is None:
            self.densities = [self.slurry.rhom]
        else:
            self.densities = densities
        if Dp is not None:
            self.slurry.Dp = Dp
        self.index = 0

    @property
    def rhom(self):
        """"The feed density at the current index"""
        return self.densities[self.index].rhom

    @rhom.setter
    def rhom(self, value):
        raise AttributeError("Cannot set rhom attribute - update the densities list")

    def feed(self, Q: float) -> ([float, float, float], Slug):
        """The cyclic feed mechanism"""
        Vls = Q / self.area
        new_slurry = deepcopy(self.slurry)
        new_slurry.rhom = self.densities[self.index]
        self.index += 1
        if self.index >= len(self.densities):
            self.index = 0

        return [0.0, 0.0, 0.0], Slug(Vls, new_slurry)
