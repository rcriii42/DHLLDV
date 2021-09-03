"""
PipeObj - Holds the pipe and Pipeline objects that manage a pipeline system

Added by R. Ramsdell 03 September, 2021
"""
import bisect
import collections
from copy import copy

from DHLLDV import DHLLDV_framework
from DHLLDV.SlurryObj import Slurry
from DHLLDV.DHLLDV_constants import gravity


Pipe = collections.namedtuple('pipe',
                              ('name', 'diameter', 'length', 'total_K', 'elev_change'),
                              )

class Pipeline():
    """Object to manage the pipeline system"""
    def __init__(self, pipe_list=None, slurry=None):
        if not slurry:
            slurry = Slurry()
        if pipe_list:
            self.pipesections = pipe_list
        else:
            self.pipesections = [Pipe('Entrance', slurry.Dp, 0, 0.5, -10.0),
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

    def calc_system_head(self, v):
        """Calculate the system head for a pipeline

        v is the velocity in m/sec

        returns a tuple, im, il"""
        rhom = self.slurry.rhom
        Hv = v**2/(2*gravity)
        delta_z = -1 * self.pipesections[0].elev_change
        Hfit = Hv       # Includes exit loss
        Hfric_m = 0
        Hfric_l = 0
        for p in self.pipesections:
            Hfit += p.total_K*Hv
            delta_z += p.elev_change
            index = bisect.bisect_left(self.slurries[p.diameter].vls_list, v)
            im = self.slurries[p.diameter].im_curves['graded_Cvt_im'][index]
            Hfric_m += im * p.length
            index = bisect.bisect_left(self.slurries[p.diameter].vls_list, v)
            il = self.slurries[p.diameter].im_curves['il'][index]
            Hfric_l += il * p.length
        return (Hfric_m + (Hfit +  + delta_z) * self.slurry.rhom,
                Hfric_l + (Hfit + + delta_z) * self.slurry.rhol)