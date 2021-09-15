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
    design_impeller: float  # m
    suction_dia: float      # m
    disch_dia: float        # m
    design_QH_curve: interpDict    # dict {flow (m/sec): head (m)}
    design_QP_curve: interpDict    # dict {flow (m/sec): power (kW}
    avail_power: float            # kW
    limited: str = 'torque'       # 'torque', 'power', 'None'
    slurry: Slurry = None

    def __post_init__(self):
        if self.slurry == None:
            self.slurry = Slurry()
        self._current_speed = self.design_speed

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

    def point(self, Q):
        """Return the head and power

        Q: flow in m3/sec

        returns a tuple: (Q: flow in m3/sec,
                          H: Head in m of water,
                          P: Power in kW,
                          N: Speed in Hz (for the power/torque limited case)"""

        speed_ratio = self._current_speed / self.design_speed
        Q0 = Q /speed_ratio
        H0 = self.design_QH_curve[Q0]
        P0 = self.design_QP_curve[Q0]

        H = H0 * speed_ratio**2 * self.slurry.rhom
        P = P0 * speed_ratio**3 * self.slurry.rhom

        if self.limited.lower() == 'torque':
            Pavail = self.avail_power * self._current_speed / self.design_speed
        else:
            Pavail = self.avail_power
        if self.limited.lower() == 'none' or P <= Pavail:
            return (Q, H, P, self._current_speed)
        else:
            n_new = self._current_speed
            while not (0.99995 < P/Pavail < 1.00005):       # Find reduced speed/head/power
                n_new *= (Pavail / P) ** 0.5
                speed_ratio = n_new / self.design_speed
                Q0 = Q / speed_ratio

                P0 = self.design_QP_curve[Q0]
                P = P0 * speed_ratio ** 3 * self.slurry.rhom
                if self.limited.lower() == 'torque':
                    Pavail = self.avail_power * n_new / self.design_speed
        H0 = self.design_QH_curve[Q0]
        H = H0 * speed_ratio ** 2 * self.slurry.rhom
        return (Q, H, P, n_new)






