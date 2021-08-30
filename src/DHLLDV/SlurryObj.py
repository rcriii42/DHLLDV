'''
SlurryObj - Holds the Slurry object that manages the inoyts and curves for a slurry and pipe

Added by R. Ramsdell 30 August, 2021
'''
import DHLLDV_framework

class Slurry():
    def __init__(self):
        self.max_index = 100
        self.Dp = 0.762  # Pipe diameter
        self.D50 = 1.0 / 1000.
        self._silt = 0
        self.epsilon = DHLLDV_constants.steel_roughness
        self._fluid = 'salt'
        self.nu = 1.0508e-6  # DHLLDV_constants.water_viscosity[20]
        self.rhol = 1.0248103  # DHLLDV_constants.water_density[20]
        self.rhos = 2.65
        self.rhoi = 1.92
        self.Cv = 0.175
        self.vls_list = [(i + 1) / 10. for i in range(self.max_index)]
        self.generate_GSD()
        self.generate_curves()

    @property
    def fluid(self):
        return self._fluid

    @fluid.setter
    def fluid(self, fluid):
        if fluid == 'salt':
            self.nu = 1.0508e-6
            self.rhol = 1.0248103
        else:
            self.nu = DHLLDV_constants.water_viscosity[20]
            self.rhol = DHLLDV_constants.water_density[20]

    @property
    def silt(self):
        return self._silt

    @silt.setter
    def silt(self, X):
        if X is None:
            X = -1
        elif X < 0:
            X = 0.0
        elif X > 1:   #In this case D85 is < 0.075 and the ELM will be invoked
            X = 0.999
        self._silt = X
        self.generate_GSD(d15_ratio=None, d85_ratio=None)

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

    def generate_GSD(self, d15_ratio=2.0, d85_ratio=2.72):

        if not d85_ratio:
            d85_ratio = self.get_dx(0.85) / self.get_dx(0.5)
        if not d15_ratio:
            d15_ratio = self.get_dx(0.5) / self.get_dx(0.15)
        temp_GSD = {0.15: self.D50 / d15_ratio,
                    0.50: self.D50,
                    0.85: self.D50 * d85_ratio,}
        if self._silt >= 0:
            temp_GSD[self._silt] = 0.075/1000
        print(temp_GSD)
        self.GSD = DHLLDV_framework.create_fracs(temp_GSD, self.Dp, self.nu, self.rhol, self.rhos)

    def get_dx(self, frac):
        """Get the grain size associated with the given frac

        TODO: To be fancy, could override self.GSD.__getitem__"""
        if frac in self.GSD:
            return self.GSD[frac]
        else:
            fracs = sorted(slurry.GSD.keys())
            logds = [log10(self.GSD[f]) for f in self.GSD]
            index = bisect.bisect(fracs, frac)
            if index >= len(fracs)-1:
                flow = fracs[-2]
                fnext = fracs[-1]
            else:
                flow = fracs[index]
                fnext = fracs[index+1]
            dlow = slurry.GSD[flow]
            dnext = slurry.GSD[fnext]
            logdthis = log10(dnext) - (log10(dnext) - log10(dlow)) * (fnext - 0.15) / (fnext - flow)
        return 10 ** logdthis

    def generate_Erhg_curves(self, vls_list, Dp, d, epsilon, nu, rhol, rhos, Cv, GSD):
        """Generate a dict with the Erhg curves

        Note assumes the GSD is already generated"""
        Erhg_obj_list = [DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cv, get_dict=True) for vls in
                         vls_list]
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
                'Cvs_from_Cvt': [DHLLDV_framework.Cvs_from_Cvt(vls, Dp, d, epsilon, nu, rhol, rhos, Cv) for vls in
                                 vls_list],
                'Cvt_Erhg': [DHLLDV_framework.Cvt_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cv) for vls in vls_list],
                'graded_Cvs_Erhg': [
                    DHLLDV_framework.Erhg_graded(GSD, vls, Dp, epsilon, nu, rhol, rhos, Cv, Cvt_eq_Cvs=False,
                                                 num_fracs=None)
                    for vls in vls_list],
                'graded_Cvt_Erhg': [
                    DHLLDV_framework.Erhg_graded(GSD, vls, Dp, epsilon, nu, rhol, rhos, Cv, Cvt_eq_Cvs=True,
                                                 num_fracs=None)
                    for vls in vls_list],
                }

    def generate_im_curves(self, Erhg_curves, Rsd, Cv, rhom):
        """Generate the im curves, given the Erhg curves"""
        c = Erhg_curves
        il_list = c['il']
        max_index = len(il_list)
        return {'il': il_list,
                'Cvs_im': [c['Cvs_Erhg'][i] * Rsd * Cv + il_list[i] for i in range(max_index)],
                'FB': [c['FB'][i] * Rsd * Cv + il_list[i] for i in range(max_index)],
                'SB': [c['SB'][i] * Rsd * Cv + il_list[i] for i in range(max_index)],
                'He': [c['He'][i] * Rsd * Cv + il_list[i] for i in range(max_index)],
                'ELM': [il_list[i] * rhom for i in range(max_index)],
                'Ho': [c['Ho'][i] * Rsd * Cv + il_list[i] for i in range(max_index)],
                'Cvt_im': [c['Cvt_Erhg'][i] * Rsd * Cv + il_list[i] for i in range(max_index)],
                'graded_Cvs_im': [c['graded_Cvs_Erhg'][i] * Rsd * Cv + il_list[i] for i in range(max_index)],
                'graded_Cvt_im': [c['graded_Cvt_Erhg'][i] * Rsd * Cv + il_list[i] for i in range(max_index)]
                }

    def generate_LDV_curves(self, Dp, d, epsilon, nu, rhol, rhos):
        cv_points = 50
        Rsd = (rhos - rhol) / rhol
        Cv_list = [(i + 1) / 100. for i in range(cv_points)]
        LDV_vls_list = [DHLLDV_framework.LDV(1, Dp, d, epsilon, nu, rhol, rhos, Cv) for Cv in Cv_list]
        LDV_il_list = [homogeneous.fluid_head_loss(vls, Dp, epsilon, nu, rhol) for vls in LDV_vls_list]
        LDV_Ergh_list = [DHLLDV_framework.Cvs_Erhg(LDV_vls_list[i], Dp, d, epsilon, nu, rhol, rhos, Cv_list[i]) for i in
                         range(cv_points)]
        LDV_im_list = [LDV_Ergh_list[i] * Rsd * Cv_list[i] + LDV_il_list[i] for i in range(cv_points)]
        return {'Cv': Cv_list,
                'vls': LDV_vls_list,
                'il': LDV_il_list,
                'Erhg': LDV_Ergh_list,
                'im': LDV_im_list,
                'regime': [f'LDV for {d * 1000:0.3f} mm particle at Cvs={Cv_list[i]}' for i in range(cv_points)]
                }
    def generate_curves(self):
        self.Erhg_curves = viewer.generate_Erhg_curves(self.vls_list, self.Dp, self.get_dx(0.5), self.epsilon,
                                                       self.nu, self.rhol, self.rhos, self.Cv, self.GSD)
        self.im_curves = viewer.generate_im_curves(self.Erhg_curves, self.Rsd, self.Cv, self.rhom)
        self.LDV_curves = viewer.generate_LDV_curves(self.Dp, self.get_dx(0.5), self.epsilon,
                                                     self.nu, self.rhol, self.rhos)
        self.LDV85_curves = viewer.generate_LDV_curves(self.Dp, self.get_dx(0.85), self.epsilon,
                                                       self.nu, self.rhol, self.rhos)