"""LagrFeeds.py - Various feed functions for the LagrPipeline"""
from copy import deepcopy
from math import pi

from DHLLDV.LagrSlug import Slug
from DHLLDV.SlurryObj import Slurry

from random import triangular


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
        return self.densities[self.index]

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


class CSDFeed(FixedDensityFeed):
    """Feed to mimic a CSD

    Swings for swing_time at the given average density
    Density drops to 1.03 during corner_time
    Swings for backswing_time at lower density (default density/2)
    Density drops to 1.03 during corner_time
    """
    def __init__(self, slurry: Slurry, density: float = None, Dp: float = None,
                 corner_time: int = 30, swing_time: int = 120, backswing_time: int = None,
                 backswing_ratio: float = 0.5):
        super().__init__(slurry, density, Dp)
        self.corner_time = corner_time
        self.swing_time = swing_time
        if backswing_time is None:
            self.backswing_time = swing_time
        else:
            self.backswing_time = backswing_time
        self.backswing_ratio = backswing_ratio
        self.index = 0

    @property
    def cycle_time(self):
        """Return the total cycle time"""
        return self.swing_time + self.corner_time + self.backswing_time + self.corner_time

    def feed(self, Q: float) -> ([float, float, float], Slug):
        """The CSD feed mechanism"""
        self.index += 1
        if self.index > self.cycle_time:
            self.index = 0

        if self.index < self.swing_time:
            min_rho = 1.03 + (self.rhom-1.03)/2
            max_rho = (self.rhom + 1.5)/2
            mode_rho = max(3 * self.rhom - min_rho - max_rho,
                           self.rhom)
            new_rhom = triangular(min_rho, max_rho, mode_rho)
        elif self.index < self.swing_time + self.corner_time:
            time_in_corner = self.swing_time + self.corner_time - self.index
            min_rho = 1.03 + (self.rhom - 1.03) / 2
            max_rho = (self.rhom + 1.5) / 2
            mode_rho = max(3 * self.rhom - min_rho - max_rho,
                           self.rhom)
            new_rhom = (triangular(min_rho, max_rho, mode_rho) * time_in_corner +
                        1.03 * (self.corner_time - time_in_corner)) / self.corner_time
        elif self.index < self.swing_time + self.corner_time + self.backswing_time:
            bs_rhom = 1.03 + (self.rhom - 1.03) * self.backswing_ratio
            min_rho = 1.03 + (bs_rhom - 1.03) / 2
            max_rho = (bs_rhom + 1.5) / 2
            mode_rho = max(3 * bs_rhom - min_rho - max_rho,
                           bs_rhom)
            new_rhom = triangular(min_rho, max_rho, mode_rho)
        else:
            time_in_corner = self.swing_time + self.corner_time + self.backswing_time + self.corner_time - self.index
            bs_rhom = 1.03 + (self.rhom - 1.03) * self.backswing_ratio
            min_rho = 1.03 + (bs_rhom - 1.03) / 2
            max_rho = (bs_rhom + 1.5) / 2
            mode_rho = max(3 * bs_rhom - min_rho - max_rho,
                           bs_rhom)
            new_rhom = (triangular(min_rho, max_rho, mode_rho) * (self.corner_time - time_in_corner) +
                        1.03 * time_in_corner) / self.corner_time

        Vls = Q / self.area
        new_slurry = deepcopy(self.slurry)
        new_slurry.rhom = new_rhom
        return [0.0, 0.0, 0.0], Slug(Vls, new_slurry)
