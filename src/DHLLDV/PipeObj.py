"""
PipeObj - Holds the pipe and Pipeline objects that manage a pipeline system

Added by R. Ramsdell 03 September, 2021
"""
import bisect
from copy import copy
from dataclasses import dataclass
from math import pi

import scipy.optimize
from DHLLDV.DHLLDV_constants import gravity
from DHLLDV.PumpObj import Pump
from DHLLDV.SlurryObj import Slurry


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
    def __init__(self, name="Pipeline", pipe_list=None, slurry=None):
        self.name = name
        if not slurry:
            slurry = Slurry()
        if pipe_list:
            self.pipesections = pipe_list
        else:
            self.pipesections = [Pipe('Entrance', slurry.Dp*34./30, 0, 0.5, -10.0),
                                 Pipe('Discharge', slurry.Dp, 1000, 1.0, 1.5)]
        self.slurry = slurry

    @property
    def num_pipesections(self):
        """The total number of pipesections"""
        return len([p for p in self.pipesections if isinstance(p, Pipe)])

    @property
    def total_length(self):
        """The total length of pipesections"""
        return sum([p.length for p in self.pipesections if isinstance(p, Pipe)])

    @property
    def total_K(self):
        """The total k of pipesections"""
        return sum([p.total_K for p in self.pipesections if isinstance(p, Pipe)])

    @property
    def total_lift(self):
        """The total elev change of pipesections"""
        return sum([p.elev_change for p in self.pipesections if isinstance(p, Pipe)])

    @property
    def num_pumps(self):
        """The total length of pipesections"""
        return len([p for p in self.pipesections if isinstance(p, Pump)])

    @property
    def total_power(self):
        """The total power of the pumps"""
        return sum([p.avail_power for p in self.pipesections if isinstance(p, Pump)])

    @property
    def Cv(self):
        return self.slurry.Cv

    @Cv.setter
    def Cv(self, Cv):
        """Allow the user to set the Cv for the entire system"""
        for s in self.slurries.values():
            s.Cv = Cv

    @property
    def slurry(self):
        return self._slurry

    @slurry.setter
    def slurry(self, s):
        self._slurry = s
        self.update_slurries()

    @property
    def pumps(self):
        """Return a list of the pumps in line"""
        return [p for p in self.pipesections if isinstance(p, Pump)]

    def update_slurries(self):
        """Update the dictionary of slurries by pipe diameter

        If self._slurry.Dp is not in the pipeline, set it to the last pipe diameter"""
        self.slurries = {self._slurry.Dp: self.slurry}
        count = 0
        for p in self.pipesections:
            if isinstance(p, Pipe) and p.diameter not in self.slurries:
                self.slurries[p.diameter] = copy(self._slurry)
                self.slurries[p.diameter].Dp = p.diameter
            elif isinstance(p, Pipe) and p.diameter == self._slurry.Dp:
                count += 1
            elif isinstance(p, Pump):
                p.slurry = self.slurry
        if count == 0:
            self._slurry.Dp = self.pipesections[-1].diameter

    def calc_system_head(self, Q):
        """Calculate the system head for a pipeline

        Q is the flow in m3/sec

        If a pipesection after the first has length 0, the elev_change is ignored

        returns a tuple: (head slurry, head water) in m water column"""
        rhom = self.slurry.rhom

        Hfit_m = 0
        Hfit_l = 0
        Hfric_m = 0     # Total system head of slurry
        Hfric_l = 0     # Total system head of water
        if self.pipesections[0].length == 0:
            # If the first pipesection has length 0, use the delta_z as the suction elevation
            # This provides an initial static head
            Hz_m = Hz_l = self.pipesections[0].elev_change * self.slurry.rhol
        else:
            Hz_m = Hz_l = 0
        Hpumps_m = 0    # Total pump head of slurry
        Hpumps_l = 0    # Total pump head of water

        for p in self.pipesections:
            if isinstance(p, Pipe):
                v = p.velocity(Q)
                Hv = v ** 2 / (2 * gravity)
                Hfit_m += p.total_K*Hv*self.slurry.rhom
                Hfit_l += p.total_K * Hv * self.slurry.rhol
                if p.length > 0:
                    Hz_m += p.elev_change * self.slurry.rhom
                    Hz_l += p.elev_change * self.slurry.rhol
                    im = self.slurries[p.diameter].im(v)
                    Hfric_m += im * p.length
                    il = self.slurries[p.diameter].il(v)
                    Hfric_l += il * p.length
            elif isinstance(p, Pump):
                Qp, Hp, Pp, np = p.point(Q, water=True)
                Hpumps_l += Hp
                Qp, Hp, Pp, np = p.point(Q)
                Hpumps_m += Hp

        Htot_m = Hfric_m + Hfit_m + Hz_m + Hv * self.slurry.rhom
        Htot_l = Hfric_l + Hfit_l + Hz_l + Hv * self.slurry.rhol

        return (Htot_m,     # System (pipeline) head losses slurry
                Htot_l,     # System (pipeline) head losses fluid
                Hpumps_l,   # Pump head slurry
                Hpumps_m)   # Pump head fluid


    def qimin(self, flow_list, precision = 0.02):
        """Find the minimum friction point in the slurry system using scipy.optimize.minimize_scalar

        flow_list is a list of flowrates (m3/sec) to consider
        precision is the flow precision (m3/sec) to use"""
        if flow_list[0] <= 0:
            lower_bound = flow_list[1] * 0.1
        else:
            lower_bound = flow_list[0] * 0.1
        bounds = [lower_bound, flow_list[-1]*2]
        def _system_head(Q):
            """Wrapper that returns only the slurry system head"""
            return self.calc_system_head(Q)[0]
        result = scipy.optimize.minimize_scalar(_system_head,
                                              bounds=[lower_bound, flow_list[-1]],
                                              method='Bounded')
        # print(f'qimin (scipy): x: {result.x} imin: {result.fun} success: {result.success} in {result.nit} iters')
        return result.x

    def find_operating_point(self, flow_list, precision=0.02):
        """Find the operating point (intersection above qimin) using scipy.optimize

                flow_list is a list of flowrates (m3/sec) to consider
                precision is the flow precision (m3/sec) to use
                Return the operating point flow (m3/sec) or qimin if no intersection
                """
        qimin = self.qimin(flow_list)
        imins = self.calc_system_head(qimin)
        if imins[0] > imins[3]:
            return qimin
        def _head_gap(q):
            """Wrapper to return the pipe - pump head gap at a certain flow"""
            Htot_m, _, _, Hpumps_m = self.calc_system_head(q)
            return Htot_m - Hpumps_m
        result = scipy.optimize.root_scalar(_head_gap, x0=qimin, x1=(qimin + flow_list[-1])/2)
        # print(f'Operating Point (scipy): Op point: {result.root} success: {result.converged} in {result.iterations} iters, flag: {result.flag}')
        return result.root

    def hydraulic_gradient(self, Q):
        """Calculate the hydraulic gradient of the pipe at the given flow

        Q: The flow in m3/sec. If Q is <= 0 return the Hydraulic Gradient at Qimin

        Returns 3 lists: pipeline locations, slurry head, pipeline elevations at each pipesection boundary"""
        if Q <= 0:
            p = Pipe(diameter=self.slurry.Dp)
            flow_list = [p.flow(v) for v in self.slurry.vls_list]
            Q = self.qimin(flow_list)
        temp_pl = Pipeline(pipe_list=[copy(p) for p in self.pipesections], slurry=self.slurry)
        loc_list = [temp_pl.total_length]
        elev_list = [temp_pl.total_lift]
        hpipe_m, hpipe_l, hpump_l, hpump_m = self.calc_system_head(Q)
        # print(f'Pump.hydraulic_gradient: {temp_pl.total_length:0.1f} {hpipe_m:0.2f} {hpump_m:0.2f}')
        head_list_m = [hpump_m - hpipe_m]
        head_list_l = [hpump_l - hpipe_l]
        while len(temp_pl.pipesections) > 1:
            p = temp_pl.pipesections.pop()
            hpipe_m, hpipe_l, hpump_l, hpump_m = temp_pl.calc_system_head(Q)
            # print(f'Pump.hydraulic_gradient: {temp_pl.total_length:0.1f} {hpipe_m:0.2f} {hpump_m:0.2f}')
            loc_list.append(temp_pl.total_length)
            head_list_m.append((hpump_m - hpipe_m))
            head_list_l.append((hpump_l - hpipe_l))
            elev_list.append(temp_pl.total_lift)
        loc_list.append(0)
        head_list_m.append(elev_list[-1]*self.slurry.rhol*-1)
        elev_list.append(elev_list[-1])
        loc_list.reverse()
        head_list_m.reverse()
        elev_list.reverse()
        return loc_list, head_list_m, elev_list

