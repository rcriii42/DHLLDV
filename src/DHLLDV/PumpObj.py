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
            assert n_new > 1/60
            speed_ratio = n_new / self.design_speed
            P = self.power_required(Q, n_new, water=water)
            Pavail = self.avail_power * n_new / self.design_speed
            print(
                f'{self.name}: Speeds: {self.current_speed * 60:0.0f}, {n_new * 60:0.0f}, {speed_ratio:0.3f}  '
                f'Power: {Pavail / 0.7457:0.3f}, {P / 0.7457:0.3f}, gap: {Pavail - P:0.3f},')
        return n_new

    def find_curve_limited_speed(self, Q, water=False):
        """Find the pump speed (Hz) at the given flow if there is a power curve

        Q is the flow rate in m3/sec
        water is True if calculating for the carrier fluid, False if for slurry
        """

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
            print(f"Finding curve limited pump speed at flow of {Q:0.3f} and density {rho:0.3f}")
            Pavail = self.design_power_curve[self._current_speed / self.design_speed]
        else:
            Pavail = self.avail_power
        if self.limited.lower() == 'none' or P <= Pavail:
            return (Q, H, P, self._current_speed)
        elif self.limited.lower() in ['torque', 'power']:
            print(f"Finding torque limited pump speed at flow of {Q:0.3f} and density {rho:0.3f}")
            n_new = self.find_torque_limited_speed(Q, water=water)
        else:
            n_new = self.find_curve_limited_speed(Q, water=water)
        speed_ratio = self._current_speed / n_new
        Q0 = Q / (speed_ratio * impeller_ratio ** 2)  # Use affinity law for trimmed impeller, WACS 3rd Edition page 207
        P = self.power_required(Q, n_new, water=water)
        H0 = self.design_QH_curve[Q0]
        H = H0 * speed_ratio ** 2 * impeller_ratio**2 * rho
        return (Q, H, P, n_new)
