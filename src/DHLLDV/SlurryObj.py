"""
SlurryObj - Holds the Slurry object that manages the inoyts and curves for a slurry and pipe

Added by R. Ramsdell 30 August, 2021
"""

import bisect
from math import log10


from . import DHLLDV_framework
from . import DHLLDV_constants
from . import DHLLDV_Utils
from . import homogeneous

class Slurry():
    def __init__(self, Dp=0.762, D50=1.0/1000., fluid='salt', Cv=0.175, max_index=100):
        self._max_index = max_index
        self._Dp = Dp
        self._epsilon = DHLLDV_constants.steel_roughness

        self.fluid = fluid  # This also sets nu and rhol
        # self.nu = 1.0508e-6  # DHLLDV_constants.water_viscosity[20]
        # self.rhol = 1.0248103  # DHLLDV_constants.water_density[20]

        self._Cv = Cv
        self._rhos = 2.65
        self.rhoi = 1.92

        self._D50 = D50
        self._GSD = None
        self.GSD_curves_dirty = True
        self.generate_GSD(d15_ratio=2.0, d85_ratio=2.72)

        self._vls_list = None
        self._Erhg_curves = None
        self._im_curves = None
        self._LDV_curves = None
        self._LDV85_curves = None
        self.curves_dirty = True

    @property
    def fluid(self):
        return self._fluid

    @fluid.setter
    def fluid(self, fluid):
        self.curves_dirty = True
        self._fluid = fluid
        if fluid == 'salt':
            self.nu = 1.0508e-6
            self.rhol = 1.0248103
        else:
            self.nu = DHLLDV_constants.water_viscosity[20]
            self.rhol = DHLLDV_constants.water_density[20]

    @property
    def Dp(self):
        return self._Dp

    @Dp.setter
    def Dp(self, Dp):
        self.curves_dirty = True
        self._Dp = Dp

    @property
    def epsilon(self):
        return self._epsilon

    @epsilon.setter
    def epsilon(self, e):
        self.curves_dirty = True
        self._epsilon = e

    @property
    def D50(self):
        return self._D50

    @D50.setter
    def D50(self, d):
        self._D50 = d
        self.GSD_curves_dirty = True
        self.curves_dirty = True

    @property
    def GSD(self):
        if self.GSD_curves_dirty:
            self.generate_GSD()
        return self._GSD

    @property
    def Cv(self):
        return self._Cv

    @Cv.setter
    def Cv(self, c):
        self.curves_dirty = True
        self._Cv = c

    @property
    def rhos(self):
        return self._rhos

    @rhos.setter
    def rhos(self, r):
        self.curves_dirty = True
        self._rhos = r

    @property
    def Rsd(self):
        return (self.rhos - self.rhol) / self.rhol

    @property
    def Cvi(self):
        return (self.rhom - self.rhol) / (self.rhoi - self.rhol)

    @property
    def rhom(self):
        return self.Cv * (self.rhos - self.rhol) + self.rhol

    @rhom.setter
    def rhom(self, Sm):
        self.Cv = (Sm - self.rhol) / (self.rhos - self.rhol)

    @property
    def max_index(self):
        return self._max_index

    @max_index.setter
    def max_index(self, imax):
        self.curves_dirty = True
        self._max_index = imax

    @property
    def vls_list(self):
        if self.curves_dirty or self._vls_list is None:
            self.generate_curves()
        return self._vls_list

    @property
    def Erhg_curves(self):
        if self.curves_dirty or self._Erhg_curves is None:
            self.generate_curves()
        return self._Erhg_curves

    @property
    def im_curves(self):
        if self.curves_dirty or self._im_curves is None:
            self.generate_curves()
        return self._im_curves

    @property
    def LDV_curves(self):
        if self.curves_dirty or self._LDV_curves is None:
            self.generate_curves()
        return self._LDV_curves

    @property
    def LDV85_curves(self):
        if self.curves_dirty or self._LDV85_curves is None:
            self.generate_curves()
        return self._LDV85_curves

    def __str__(self):
        """String representation of the slurry"""
        out_string = [f'Slurry in {self.Dp:0.3f} m pipe',
                      f'D15/D50/D85 (mm): {self.get_dx(0.15)*1000:0.3f}/{self.get_dx(0.50)*1000:0.3f}/{self.get_dx(0.85)*1000:0.3f}',
                      f'Solids Concentration (Cvs, -): {self.Cv:0.3f}',
                      f'Insitu Concentration (Cvi, -): {self.Cvi:0.3f}',
                      f'Fluid Density (Rhos, ton/m3): {self.rhol:0.3f}',
                      f'Solids Density (Rhos, ton/m3): {self.rhos:0.3f}',
                      f'Slurry Density (Rhom, ton/m3): {self.rhom:0.3f}',
                      f'Insitu Density (Rhoi, ton/m3): {self.rhoi:0.3f}',
                      ]
        return "\n".join(out_string)

    def generate_GSD(self, d15_ratio=None, d85_ratio=None):
        """Generate the full GSD based on the given D50 and slope

        d15_ratio = d50/d15 (-) if 0 or None, use the current ratio
        d85_ratio = d85/d50 (-) if 0 or None, use the current ratio"""
        self.GSD_curves_dirty = False
        if not d85_ratio:
            d85_ratio = self.get_dx(0.85) / self.get_dx(0.5)
        if not d15_ratio:
            d15_ratio = self.get_dx(0.5) / self.get_dx(0.15)
        temp_GSD = {0.15: self.D50 / d15_ratio,
                    0.50: self.D50,
                    0.85: self.D50 * d85_ratio,}
        self._GSD = DHLLDV_framework.create_fracs(temp_GSD, self.Dp, self.nu, self.rhol, self.rhos)
        self.curves_dirty = True

    def get_dx(self, frac):
        """Get the grain size associated with the given frac

        TODO: To be fancy, could override self.GSD.__getitem__"""
        if frac in self.GSD:
            return self.GSD[frac]
        else:
            fracs = sorted(self.GSD.keys())
            log10s = [log10(self.GSD[x]) for x in fracs]
            log10_iterp = DHLLDV_Utils.interpDict(*zip(fracs, log10s), extrapolate_low=True)
            logdthis = log10_iterp[frac]
        return 10 ** logdthis

    def il(self, vls):
        """Return the il at the given velocity. Just a wrapper around homogeneous.fluid_head_loss

        vls = Velocity (m/sec)"""
        return homogeneous.fluid_head_loss(vls, self.Dp, self.epsilon, self.nu, self.rhol)

    def Erhg(self, vls):
        """Return the Erhg at the given velocity, GSD, Cvt. Just a wrapper around Erhg_graded

        vls = Velocity (m/sec)
        Assumes the GSD is already generated"""
        return DHLLDV_framework.Erhg_graded(self.GSD, vls, self.Dp, self.epsilon,
                                            self.nu, self.rhol, self.rhos,
                                            self.Cv, Cvt_eq_Cvs=True, num_fracs=None)

    def im(self, vls):
        """Return the im at the given velocity, GSD, Cvt.

        vls = Velocity (m/sec)
        Assumes the GSD is already generated"""
        return self.Erhg(vls) * self.Rsd * self.Cv + self.il(vls)

    def generate_Erhg_curves(self):
        """Generate a dict with the Erhg curves

        Note assumes the GSD is already generated"""
        Erhg_obj_list = [DHLLDV_framework.Cvs_Erhg(vls, self.Dp, self.D50, self.epsilon, self.nu, self.rhol, self.rhos, self.Cv, get_dict=True) for vls in
                         self.vls_list]
        il_list = [Erhg_obj['il'] for Erhg_obj in Erhg_obj_list]
        # Erhg for the ELM is just the il
        return {'Erhg_objects': Erhg_obj_list,
                'il': il_list,
                'Cvs_Erhg': [Erhg_obj[Erhg_obj['regime']] for Erhg_obj in Erhg_obj_list],
                'FB': [Erhg_obj['FB'] for Erhg_obj in Erhg_obj_list],
                'SB': [Erhg_obj['SB'] for Erhg_obj in Erhg_obj_list],
                'He': [Erhg_obj['He'] for Erhg_obj in Erhg_obj_list],
                'Ho': [Erhg_obj['Ho'] for Erhg_obj in Erhg_obj_list],
                'Cvs_regime': [Erhg_obj['regime'] for Erhg_obj in Erhg_obj_list],
                'Cvs_from_Cvt': [DHLLDV_framework.Cvs_from_Cvt(vls, self.Dp, self.D50, self.epsilon, self.nu, self.rhol, self.rhos, self.Cv) for vls in
                                 self.vls_list],
                'Cvt_Erhg': [DHLLDV_framework.Cvt_Erhg(vls, self.Dp, self.D50, self.epsilon, self.nu, self.rhol, self.rhos, self.Cv) for vls in self.vls_list],
                'graded_Cvs_Erhg': [
                    DHLLDV_framework.Erhg_graded(self.GSD, vls, self.Dp, self.epsilon, self.nu, self.rhol, self.rhos, self.Cv, Cvt_eq_Cvs=False,
                                                 num_fracs=None)
                    for vls in self.vls_list],
                'graded_Cvt_Erhg': [
                    DHLLDV_framework.Erhg_graded(self.GSD, vls, self.Dp, self.epsilon,
                                                 self.nu, self.rhol, self.rhos, self.Cv,
                                                 Cvt_eq_Cvs=True, num_fracs=None)
                    for vls in self.vls_list],
                }

    def generate_im_curves(self):
        """Generate the im curves, given the Erhg curves"""
        c = self.Erhg_curves
        il_list = c['il']
        return {'il': il_list,
                'Cvs_im': [c['Cvs_Erhg'][i] * self.Rsd * self.Cv + il_list[i] for i in range(self.max_index)],
                'FB': [c['FB'][i] * self.Rsd * self.Cv + il_list[i] for i in range(self.max_index)],
                'SB': [c['SB'][i] * self.Rsd * self.Cv + il_list[i] for i in range(self.max_index)],
                'He': [c['He'][i] * self.Rsd * self.Cv + il_list[i] for i in range(self.max_index)],
                'ELM': [il_list[i] * self.rhom for i in range(self.max_index)],
                'Ho': [c['Ho'][i] * self.Rsd * self.Cv + il_list[i] for i in range(self.max_index)],
                'Cvt_im': [c['Cvt_Erhg'][i] * self.Rsd * self.Cv + il_list[i] for i in range(self.max_index)],
                'graded_Cvs_im': [c['graded_Cvs_Erhg'][i] * self.Rsd * self.Cv + il_list[i] for i in range(self.max_index)],
                'graded_Cvt_im': [c['graded_Cvt_Erhg'][i] * self.Rsd * self.Cv + il_list[i] for i in range(self.max_index)]
                }

    def generate_LDV_curves(self, d):
        cv_points = 50
        Cv_list = [(i + 1) / 100. for i in range(cv_points)]
        LDV_vls_list = [DHLLDV_framework.LDV(1, self.Dp, d, self.epsilon, self.nu, self.rhol, self.rhos, Cv) for Cv in Cv_list]
        LDV_il_list = [homogeneous.fluid_head_loss(vls, self.Dp, self.epsilon, self.nu, self.rhol) for vls in LDV_vls_list]
        LDV_Ergh_list = [DHLLDV_framework.Cvs_Erhg(LDV_vls_list[i], self.Dp, d, self.epsilon, self.nu, self.rhol, self.rhos, Cv_list[i]) for i in
                         range(cv_points)]
        LDV_im_list = [LDV_Ergh_list[i] * self.Rsd * Cv_list[i] + LDV_il_list[i] for i in range(cv_points)]
        return {'Cv': Cv_list,
                'vls': LDV_vls_list,
                'il': LDV_il_list,
                'Erhg': LDV_Ergh_list,
                'im': LDV_im_list,
                'regime': [f'LDV for {d * 1000:0.3f} mm particle at Cvs={Cv_list[i]}' for i in range(cv_points)]
                }
    def generate_curves(self):
        if self.GSD_curves_dirty:
            self.generate_GSD()
        self.curves_dirty = False   # set it at the top so curves generate only once
        self._vls_list = [(i + 1) / 10. for i in range(self.max_index)]
        self._Erhg_curves = self.generate_Erhg_curves()
        self._im_curves = self.generate_im_curves()
        self._LDV_curves = self.generate_LDV_curves(self.get_dx(0.5))
        self._LDV85_curves = self.generate_LDV_curves(self.get_dx(0.85))


