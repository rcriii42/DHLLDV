"""DriverObj.py - Object to manage a pump driver (engine or motor).

Added by R. Ramsdell 23 June 2022"""

from dataclasses import dataclass

from DHLLDV.DHLLDV_Utils import interpDict

@dataclass
class Driver():
    """Implement a pump driver (motor or engine) with an associated speed (Hz)- power (kW) curve"""

    name: str
    design_power_curve: interpDict

    def power(self, speed):
        """Return the power (kW) at the given speed (Hz)"""
        return self.design_power_curve[speed]

    @property
    def design_speed(self):
        """Return the maximum speed (Hz)"""
        return max(self.design_power_curve.keys())

    @property
    def design_power(self):
        """Return the power (kW) at the maximum speed"""
        return self.power(self.design_speed)

    @property
    def minimum_speed(self):
        """Return the minimum speed of the driver"""
        return min(self.design_power_curve.keys())