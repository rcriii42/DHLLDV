"""
PumpObj: Object to simulate a pump and driver

Added by R. Ramsdell 03 September, 2021
"""
from dataclasses import dataclass

from DHLLDV.DHLLDV_constants import gravity
from DHLLDV.DHLLDV_Utils import interpDict
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
    design_power_curve: interpDict or None = None   # dict {design_speed/n (-): power (kW)
    slurry: Slurry = None

    def __post_init__(self):
        if self.slurry == None:
            self.slurry = Slurry()
        self._current_speed = self.design_speed
        self._current_impeller = self.design_impeller
        self.design_QH_curve.extrapolate_high = True
        self.design_QP_curve.extrapolate_high = True

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
        self._current_speed = N

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

    def find_torque_limited_speed(self, Q, water=False):
        """Find the pump speed (Hz) at the given flow if torque limited

        Q is the flow rate in m3/sec
        water is True if calculating for the carrier fluid, False if for slurry
        """
        n_new = self._current_speed
        P = self.power_required(Q, self.current_speed, water=water)
        Pavail = self.avail_power * self._current_speed / self.design_speed
        if Pavail >= P:
            return n_new
        while not (-0.1 < Pavail - P < 0.1):
            n_new *= (Pavail / P) ** 0.5
            speed_ratio = n_new / self.design_speed
            P = self.power_required(Q, self.current_speed, water=water)
            Pavail = self.avail_power * self._current_speed / self.design_speed

    def find_curve_limited_speed(self, Q, water=False):
        """Find the pump speed (Hz) at the given flow if there is a power curve

        Q is the flow rate in m3/sec
        water is True if calculating for the carrier fluid, False if for slurry
        """
        print(f"Finding curve limited pump speed at flow of {Q:0.3f}")
        n_new = self._current_speed
        speed_ratio_new = n_new / self.design_speed
        P = self.power_required(Q, self.current_speed, water=water)
        Pavail = self.design_power_curve[speed_ratio_new]
        if Pavail >= P:
            return n_new
        speed_ratio_high = False
        gaps = []
        for speed_ratio_low in self.design_power_curve.keys():
            if not speed_ratio_high:
                speed_ratio_high = speed_ratio_low
                continue
            n_high = speed_ratio_high * self.design_speed
            gap_high = self.design_power_curve[speed_ratio_high] - self.power_required(Q, n_high, water=water)
            n_low = speed_ratio_low * self.design_speed
            gap_low = self.design_power_curve[speed_ratio_low] - self.power_required(Q, n_low, water=water)
            gaps.append([n_high, gap_high, gap_low])
            if gap_low >= 0:
                break
            speed_ratio_high = speed_ratio_low
        if speed_ratio_high == speed_ratio_low: # There was no intersection
            return n_low
        n_new = (n_high + n_low) / 2
        speed_ratio_new = n_new / self.design_speed
        P = self.power_required(Q, n_new, water=water)
        Pavail = self.design_power_curve[speed_ratio_new]
        print(f'{self.name}: Speeds: {self.current_speed * 60:0.0f}, {n_new * 60:0.0f}, {speed_ratio_new:0.3f} gap: {Pavail - P:0.3f}, '
              f'Power: {Pavail / 0.7457:0.3f}, {P / 0.7457:0.3f}, {(Pavail - P) / 0.7457:0.3f} ')
        while not (-0.1 < Pavail - P < 0.1):
            gap_new = Pavail - P
            if gap_new < 0:
                n_high = n_new
            else:
                n_low = n_new
            n_new = (n_high + n_low) / 2
            speed_ratio_new = n_new / self.design_speed
            P = self.power_required(Q, n_new, water=water)
            Pavail = self.design_power_curve[speed_ratio_new]
            print(f'{self.name}: Speeds: {self.current_speed * 60:0.0f}, {n_new * 60:0.0f}, {speed_ratio_new:0.3f} gap: {Pavail - P:0.3f}, '
                  f'Power: {Pavail / 0.7457:0.3f}, {P / 0.7457:0.3f}, {(Pavail - P) / 0.7457:0.3f} ')
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

        if self.limited.lower() == 'torque':
            Pavail = self.avail_power * self._current_speed / self.design_speed
        elif self.limited.lower() == 'curve':
            Pavail = self.design_power_curve[self._current_speed / self.design_speed]
        else:
            Pavail = self.avail_power
        if self.limited.lower() == 'none' or P <= Pavail:
            return (Q, H, P, self._current_speed)
        elif self.limited.lower() in ['torque', 'power']:
            n_new = self.find_torque_limited_speed(Q, water=water)
        else:
            n_new = self.find_curve_limited_speed(Q, water)
        # Find reduced speed/head/power
            # print(f"Finding pump speed at flow of {Q:0.3f}")
            # n_new = self._current_speed
            # n_gap = n_gap0 = 0.02 # The range of speed (Hz) to use when calculating the derivative
            # n_list = []
            # max_iters = 100
            # while not (-0.1 < Pavail - P < 0.1):
            #
            #     else:   # If pump curve given, use Newton-Rhapson method to set Pavail-P to 0
            #         # First the high and low n for calculating the derivative
            #         # speed_ratio = n_new / self.design_speed
            #         # speed_ratio_high = min(speed_ratio + n_gap/2, max(self.design_power_curve.keys()))
            #         # n_high = self.design_speed * speed_ratio_high
            #         # speed_ratio_low = max(speed_ratio_high - n_gap, min(self.design_power_curve.keys()))
            #         # n_low = self.design_speed * speed_ratio_low
            #         # # Next the derivative
            #         # gap_high = self.design_power_curve[speed_ratio_high] - power_required(n_high)
            #         # gap_low = self.design_power_curve[speed_ratio_low] - power_required(n_low)
            #         # slope = (gap_high - gap_low) / (n_high - n_low)
            #         # n_new = n_new - (self.design_power_curve[speed_ratio] - power_required(n_new))/slope
            #         # speed_ratio = n_new / self.design_speed
            #         # if speed_ratio > max(self.design_power_curve.keys()):
            #         #     n_gap *= 2
            #         #     speed_ratio = speed_ratio_low
            #         #     n_new = self.design_speed * speed_ratio
            #         # elif speed_ratio < min(self.design_power_curve.keys()):
            #         #     speed_ratio = speed_ratio_high
            #         #     n_new = self.design_speed * speed_ratio
            #         #     n_gap *= 2
            #         # elif n_gap > n_gap0:
            #         #     n_gap /= 2
            #
            #
            #
            #
            #     P = power_required(n_new)
            #     if self.limited.lower() == 'torque':
            #         Pavail = self.avail_power * speed_ratio
            #     elif self.limited.lower() == 'curve':
            #         Pavail = self.design_power_curve[speed_ratio]
            #     # n_list.append((n_new, Pavail, P))
            #     # if len(n_list) > max_iters:
            #     #     n_new, Pavail, P = min(n_list, key=lambda t: abs(t[1]-t[2]))
            #     #     speed_ratio = n_new / self.design_speed
            #     #     print(f'Pump.point Max Iterations at flow of {Q:0.3f}: Speeds: {self.current_speed * 60:0.0f}, '
            #     #           f'{n_new * 60:0.0f}, {speed_ratio:0.3f} gap: {n_gap:0.3f}, '
            #     #           f'Power: {Pavail / 0.7457:0.3f}, {P / 0.7457:0.3f}, {(Pavail - P) / 0.7457:0.3f}')
            #     #     # print(n_list)
            #     #     break
        P = self.power_required(Q, n_new, water=water)
        H0 = self.design_QH_curve[Q0]
        H = H0 * speed_ratio ** 2 * impeller_ratio**2 * rho
        return (Q, H, P, n_new)
