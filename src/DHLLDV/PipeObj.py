"""
PipeObj - Holds the pipe and Pipeline objects that manage a pipeline system

Added by R. Ramsdell 03 September, 2021
"""
import bisect
import collections
from copy import copy
from dataclasses import dataclass
from math import pi

from DHLLDV import DHLLDV_framework
from DHLLDV.PumpObj import Pump
from DHLLDV.SlurryObj import Slurry
from DHLLDV.DHLLDV_constants import gravity

@dataclass
class Pipe():
    """Object to manage the data about a section of pipe"""
    name: str = 'Pipe Section'
    diameter: float = 0.762
    length: float = 1.0
    total_K: float = 0.0
    elev_change: float = 0.0

    def flow(self, v):
        """Return the flow for the associated velocity

        v is velocity in m/sec
        returns flow in m3/sec"""
        return v * (self.diameter/2)**2 * pi

    def velocity(self, Q):
        """Return the velocity for the associated flow

                Q is the flow in m3/sec
                returns velocity in m/sec"""
        return Q / ((self.diameter / 2) ** 2 * pi)

class Pipeline():
    """Object to manage the pipeline system"""
    def __init__(self, pipe_list=None, slurry=None):
        if not slurry:
            slurry = Slurry()
        if pipe_list:
            self.pipesections = pipe_list
        else:
            self.pipesections = [Pipe('Entrance', slurry.Dp*34./30, 0, 0.5, -10.0),
                                 Pipe('Discharge', slurry.Dp, 1000, 1.0, 1.5)]
        self.slurry = slurry

    @property
    def Cv(self):
        return self.slurry.Cv

    @Cv.setter
    def Cv(self, Cv):
        """Allow the user to set the Cv for the entire system"""
        for s in self.slurries.values():
            s.Cv = Cv
            s.generate_curves()

    @property
    def slurry(self):
        return self._slurry

    @slurry.setter
    def slurry(self, s):
        self._slurry = s
        self.slurries = {self._slurry.Dp: self.slurry}
        for p in self.pipesections:
            if p.diameter not in self.slurries:
                self.slurries[p.diameter] = copy(self._slurry)
                self.slurries[p.diameter].Dp = p.diameter
                self.slurries[p.diameter].generate_curves()

    def calc_system_head(self, Q):
        """Calculate the system head for a pipeline

        Q is the flow in m3/sec

        returns a tuple: (head slurry, head water) in m water column"""
        rhom = self.slurry.rhom

        delta_z = -1 * self.pipesections[0].elev_change
        Hfit = 0
        Hfric_m = 0     # Total system head of slurry
        Hfric_l = 0     # Total system head of water
        Hpumps_m = 0    # Total pump head of slurry
        Hpumps_l = 0    # Total pump head of water
        for p in self.pipesections:
            if isinstance(p, Pipe):
                v = p.velocity(Q)
                Hv = v ** 2 / (2 * gravity)
                Hfit += p.total_K*Hv
                delta_z += p.elev_change
                index = bisect.bisect_left(self.slurries[p.diameter].vls_list, v)
                im = self.slurries[p.diameter].im_curves['graded_Cvt_im'][index]
                Hfric_m += im * p.length
                index = bisect.bisect_left(self.slurries[p.diameter].vls_list, v)
                il = self.slurries[p.diameter].im_curves['il'][index]
                Hfric_l += il * p.length
            elif isinstance(p, Pump):
                temp_rhom = p.slurry.rhom
                p.slurry.rhom = p.slurry.rhol
                Qp, Hp, Pp, np = p.point(Q)
                Hpumps_l += Hp
                p.slurry.rhom = temp_rhom
                Qp, Hp, Pp, np = p.point(Q)
                Hpumps_m += Hp

        return (Hfric_m + (Hfit + delta_z + Hv) * self.slurry.rhom,
                Hfric_l + (Hfit + delta_z + Hv) * self.slurry.rhol)