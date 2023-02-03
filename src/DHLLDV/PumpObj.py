"""
PumpObj: Object to simulate a pump and driver

Added by R. Ramsdell 03 September, 2021
"""
from dataclasses import dataclass, fields

import scipy.optimize

from DHLLDV.DHLLDV_constants import gravity
from DHLLDV.DHLLDV_Utils import interpDict
from DHLLDV.DriverObj import Driver
from DHLLDV.SlurryObj import Slurry


@dataclass
class Pump():
    """Model a pump and driver"""
    name: str
    design_speed: float     # Hz
    design_impeller: float  # impeller dia in m
    suction_dia: float      # m
    disch_dia: float        # m
    design_QH_curve: interpDict    # dict {flow (m/sec): head (m)}
    design_QP_curve: interpDict    # dict {flow (m/sec): power (kW}
    avail_power: float            # kW
    limited: str = 'torque'       # 'torque', 'power', 'curve', 'None'
    driver: Driver or None = None   # dict {design_speed/n (-): power (kW)
    driver_name: str or None = None
    gear_ratio: float = 1.0
    slurry: Slurry = None

    def __post_init__(self):
        if self.slurry == None:
            self.slurry = Slurry()
        self._current_speed = self.design_speed
        self._current_impeller = self.design_impeller
        self._max_driver_speed = self.design_speed  # The speed at max power or the power curve basis
        self.design_QH_curve.extrapolate_high = True
        self.design_QP_curve.extrapolate_high = True
        if self.limited != 'curve':
            self.driver_name = f'{self.limited} driver {self.avail_power:0.1f} at {self.design_speed:0.3f}'

    def __str__(self):
        """Only print parameters that are string or float. Print the names of the driver and slurry"""
        s = [f'Pump(name="{self.name}", ']
        for f in fields(self):
            if f.type == float:
                s.append(f'{f.name}={getattr(self, f.name):0.4f}, ')
            elif f.type == int:
                s.append(f'{f.name}={getattr(self, f.name)}, ')
            elif f.type == Driver and getattr(self, f.name) is not None:
                s.append(f'{f.name}="{getattr(self, f.name).name}", ')
            elif f.type == Slurry and getattr(self, f.name) is not None:
                slurry = getattr(self, f.name)
                if slurry._name:
                    s.append(f'{f.name}="{slurry.name}", ')
                else:
                    d15 = slurry.get_dx(0.15)*1000
                    d50 = slurry.get_dx(0.50)*1000
                    d85 = slurry.get_dx(0.85)*1000
                    slurry_name = f'Slurry of {d15:0.3f}/{d50:0.3f}/{d85:0.3f} mm sand in {slurry.fluid} water'
                    s.append(f'{f.name}="{slurry_name}", ')
        s.append(')')
        return ''.join(s)

    def efficiency(self, q):
        """Return the efficiency of the pump based on the current speed"""
        Q, H, P, N = self.point(q)
        return gravity * q * H / P

    @property
    def current_speed(self):
        """Get the current speed in Hz"""
        return self._current_speed

    @current_speed.setter
    def current_speed(self, N):
        """Set the current speed

        N: New speed in Hz"""
        if N > self._max_driver_speed:
            print(f'WARNING: Setting current speed of {N:0.4f} to greater than max_driver_speed of {self._max_driver_speed:0.4f}')
        self._current_speed = N

    @property
    def max_driver_speed(self):
        """Get the max driver speed in Hz"""
        return self._max_driver_speed

    @max_driver_speed.setter
    def max_driver_speed(self, N):
        """Set the max_driver speed

        N: New speed in Hz"""
        self._max_driver_speed = N
        self._current_speed = self._max_driver_speed

    @property
    def current_impeller(self):
        """Get the current impeller in m"""
        return self._current_impeller

    @current_impeller.setter
    def current_impeller(self, impeller):
        """Set the current impeller

        impeller: New impeller in m"""
        self._current_impeller = impeller

    def power_required(self, Q, n, water=False):
        """Calculate the power required (kW) at the given flow and speed

        Q is flow in m3/sec
        n is pump speed in Hz
        water is True if calculating for the carrier fluid, False if for slurry"""
        if water:
            rho = self.slurry.rhol
        else:
            rho = self.slurry.rhom
        if n == 0:
            return 0
        speed_ratio = n / self.design_speed
        impeller_ratio = self.current_impeller / self.design_impeller
        Q0 = Q / (speed_ratio * impeller_ratio ** 2)  # Use affinity law for trimmed impeller, WACS 3rd Edition page 207
        P0 = self.design_QP_curve[Q0]
        return P0 * speed_ratio**3 * impeller_ratio**5 * rho

    def power_available(self, n):
        """Return the available power at the given speed"""
        match self.limited:
            case 'torque':
                return self.avail_power * n / self._max_driver_speed
            case 'power':
                return self.avail_power
            case 'curve':
                return self.driver.power(n*self.gear_ratio)
            case other:
                speed_ratio = n / self._max_driver_speed
                impeller_ratio = self.current_impeller / self.design_impeller
                return max(self.design_QP_curve.values()) * speed_ratio**3 * impeller_ratio**5 * self.slurry.rhom + 1

    def find_torque_limited_speed(self, Q, water=False):
        """Find the pump speed (Hz) at the given flow if torque limited

        Q is the flow rate in m3/sec
        water is True if calculating for the carrier fluid, False if for slurry
        """

        n_new = self._current_speed
        P = self.power_required(Q, self.current_speed, water=water)
        Pavail = self.power_available(n_new)
        if Pavail >= P:
            return n_new
        while not (-0.1 < Pavail - P < 0.1):
            n_new *= (Pavail / P) ** 0.5
            assert n_new > 1/60
            P = self.power_required(Q, n_new, water=water)
            Pavail = self.power_available(n_new)
        return n_new

    def find_power_limited_speed(self, Q, water=False):
        """Find the pump speed (Hz) at the given flow if power limited (constant power)

        Q is the flow rate in m3/sec
        water is True if calculating for the carrier fluid, False if for slurry
        """

        n_new = self._current_speed
        P = self.power_required(Q, self.current_speed, water=water)
        Pavail = self.avail_power
        if Pavail >= P:
            return n_new
        while not (-0.1 < Pavail - P < 0.1):
            n_new *= (Pavail / P) ** 0.5
            assert n_new > 1 / 60
            P = self.power_required(Q, n_new, water=water)
        return n_new

    def find_curve_limited_speed(self, Q, water=False):
        return self.find_curve_limited_speed_root_scalar(Q, water)

    def find_curve_limited_speed_root_scalar(self, Q, water=False):
        """Find the pump speed (Hz) at the given flow if there is a power curve

        Q is the flow rate in m3/sec
        water is True if calculating for the carrier fluid, False if for slurry
        """
        def _power_gap(n):
            """Wrapper to return the avail - required power gap at a certain speed"""
            return self.power_available(n) - self.power_required(Q, n, water=water)

        if _power_gap(self.design_speed) >= 0:
            return self.design_speed

        speeds = reversed([p/self.gear_ratio for p in self.driver.design_power_curve.keys()])

        n_high = next(speeds)
        n_low = next(speeds)
        while _power_gap(n_low) < 0:
            n_high = n_low
            n_low = next(speeds)

        result = scipy.optimize.root_scalar(_power_gap,
                                            bracket=[n_low, n_high])
        # print(f'Operating Point (scipy): Op point: {result.root} success: {result.converged} in {result.iterations} iters, flag: {result.flag}')
        if result.converged:
            return result.root


    def find_curve_limited_speed_old(self, Q, water=False):
        """Find the pump speed (Hz) at the given flow if there is a power curve

        Q is the flow rate in m3/sec
        water is True if calculating for the carrier fluid, False if for slurry
        """

        n_new = self._current_speed
        speed_ratio_new = n_new / self.design_speed
        P = self.power_required(Q, self.current_speed, water=water)
        Pavail = self.driver.power(n_new * self.gear_ratio)
        if Pavail >= P:
            return n_new
        n_low = False
        gaps = []
        for n_high in self.driver.design_power_curve.keys():
            n_high /= self.gear_ratio
            if not n_low:
                n_low = n_high
                continue
            gap_high = self.driver.power(n_high*self.gear_ratio) - self.power_required(Q, n_high, water=water)
            gap_low = self.driver.power(n_low*self.gear_ratio) - self.power_required(Q, n_low, water=water)
            gaps.append([n_low, n_high, gap_low, gap_high])
            if gap_low >= 0:
                break
            n_high = n_low
        if n_high == n_low: # There was no intersection
            return n_low
        n_new = (n_high + n_low) / 2
        # speed_ratio_new = n_new / self.design_speed
        P = self.power_required(Q, n_new, water=water)
        Pavail = self.driver.power(n_new * self.gear_ratio)
        while not (-0.1 < Pavail - P < 0.1):
            gap_new = Pavail - P
            if gap_new < 0:
                n_low = n_new
            else:
                n_high = n_new
            n_new = (n_high + n_low) / 2
            # speed_ratio_new = n_new / self.design_speed
            P = self.power_required(Q, n_new, water=water)
            Pavail = self.driver.power(n_new * self.gear_ratio)
            if n_low/n_high > 0.999:
                break
        return n_new

    def point(self, Q, water=False):
        """Return the head and power

        Q: flow in m3/sec
        water: If true return the head for water, else head for slurry

        returns a tuple: (Q: flow in m3/sec,
                          H: Head in m of water,
                          P: Power in kW,
                          N: Speed in Hz (for the power/torque limited case)"""

        if water:
            rho = self.slurry.rhol
        else:
            rho = self.slurry.rhom
        speed_ratio = self._current_speed / self.design_speed
        impeller_ratio = self._current_impeller / self.design_impeller
        Q0 = Q / (speed_ratio * impeller_ratio**2) # Use affinity law for trimmed impeller, WACS 3rd Edition page 207
        H0 = self.design_QH_curve[Q0]
        H = H0 * speed_ratio**2 * impeller_ratio**2 * rho

        P = self.power_required(Q, self.current_speed, water=water)

        if self.limited.lower() == 'none' or P <= self.power_available(self._current_speed):
            return (Q, H, P, self._current_speed)
        elif self.limited.lower() == 'torque':
            n_new = self.find_torque_limited_speed(Q, water=water)
        elif self.limited.lower() == 'power':
            n_new = self.find_power_limited_speed(Q, water=water)
        else:
            n_new = self.find_curve_limited_speed(Q, water=water)
        speed_ratio = n_new / self.design_speed
        Q0 = Q / (speed_ratio * impeller_ratio ** 2)  # Use affinity law for trimmed impeller, WACS 3rd Edition page 207
        P = self.power_required(Q, n_new, water=water)
        H0 = self.design_QH_curve[Q0]
        H = H0 * speed_ratio ** 2 * impeller_ratio**2 * rho
        return (Q, H, P, n_new)
