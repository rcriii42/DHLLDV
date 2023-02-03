"""
viewer_Wilson - Compare the DHLLDV and Wilson curves for a given sand
Created on Oct 15, 2016

@author: rcriii
"""

from DHLLDV import DHLLDV_constants
from DHLLDV import DHLLDV_framework
from DHLLDV import homogeneous

from Wilson import Wilson_Stratified, Wilson_V50

try:
    import matplotlib.pyplot as plt
except ImportError:
    print('matplotlib not found')
    plt = None


if __name__ == '__main__':
    Dp = 0.762  # Pipe diameter
    d = 0.2/1000.
    GSD = {0.15: d / 1.5,
           0.50: d,
           0.85: d * 1.5}
    epsilon = DHLLDV_constants.steel_roughness
    nu = 1.0508e-6  # DHLLDV_constants.water_viscosity[20]
    rhos = 2.65
    rhol = 1.0248103  # DHLLDV_constants.water_density[20]
    Rsd = (rhos - rhol)/rhol
    Cv = 0.10
    rhom = Cv*(rhos-rhol)+rhol

    num_points = 100
    vls_list = [(i+1)/10. for i in range(num_points)]

    # The DHLLDV model for the given material
    Erhg_obj_list = [DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cv, get_dict=True)
                     for vls in vls_list]
    il_list = [Erhg_obj['il'] for Erhg_obj in Erhg_obj_list]
    Cvt_Erhg_list = [DHLLDV_framework.Cvt_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cv) for vls in vls_list]
    graded_Cvt_Erhg_list = [DHLLDV_framework.Erhg_graded(GSD, vls, Dp, epsilon, nu, rhol, rhos, Cv, Cvt_eq_Cvs=True)
                            for vls in vls_list]

    # Wilson Coarse for the D50 and D85
    musf = DHLLDV_constants.musf
    Wilson_Stratified_ERHG_list_50 = [Wilson_Stratified.Erhg(Vls, Dp, GSD[0.5], epsilon, nu, rhol, rhos, musf, Cv)
                                      for Vls in vls_list]
    Wilson_Stratified_ERHG_list_85 = [Wilson_Stratified.Erhg(Vls, Dp, GSD[0.85], epsilon, nu, rhol, rhos, musf, Cv)
                                      for Vls in vls_list]

    # Wilson V50 (heterogeneous)
    Wilson_V50_ERHG_list = [Wilson_V50.Erhg(Vls, Dp, GSD[0.50], GSD[0.85], epsilon, nu, rhol, rhos, musf)
                            for Vls in vls_list]

    # LDV curves
    Cv_list = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]
    LDV_by_Cv = [DHLLDV_framework.LDV(None, Dp, d, epsilon, nu, rhol, rhos, Cvthis)
                 for Cvthis in Cv_list]
    il_Erhg_im = []
    for v, Cvthis in zip(LDV_by_Cv, Cv_list):
        return_list = DHLLDV_framework.Erhg_graded(GSD, v, Dp, epsilon, nu, rhol, rhos, Cvthis,
                                                   Cvt_eq_Cvs=True, get_dict=True)
        il_Erhg_im.append([return_list['il'],
                           return_list['Erhg'],
                           return_list['Erhg'] * Rsd * Cvthis + return_list['il']])
    LDV_by_Cv_ils, LDV_by_Cv_Erhg, LDV_by_Cv_im = list(zip(*il_Erhg_im))

    d_list = DHLLDV_framework.Erhg_graded(GSD, 6.0, Dp, epsilon, nu, rhol, rhos,
                                          Cv, Cvt_eq_Cvs=True, get_dict=True)['ds']
    print([f'{d*1000:0.2f}' for d in d_list])
    LDV_by_d = [DHLLDV_framework.LDV(None, Dp, dthis, epsilon, nu, rhol, rhos, Cv) for dthis in d_list]
    il_Erhg_im = []
    for v, dthis in zip(LDV_by_d, d_list):
        return_list = DHLLDV_framework.Erhg_graded(GSD, v, Dp, epsilon, nu, rhol, rhos,
                                                   Cv, Cvt_eq_Cvs=True, get_dict=True)
        Erhg = return_list['Erhg']
        il_Erhg_im.append([return_list['il'],
                           Erhg,
                           Erhg * Rsd * Cv + return_list['il']])
    LDV_by_d_ils, LDV_by_d_Erhg, LDV_by_d_im = list(zip(*il_Erhg_im))

    v_ldv = DHLLDV_framework.LDV(None, Dp, d, epsilon, nu, rhol, rhos, Cv)
    il_ldv = homogeneous.fluid_head_loss(v_ldv, Dp, epsilon, nu, rhol)
    Erhg_ldv = DHLLDV_framework.Erhg_graded(GSD, v_ldv, Dp, epsilon, nu, rhol, rhos,
                                            Cv, Cvt_eq_Cvs=True)
    im_ldv = Erhg_ldv * Rsd * Cv + il_ldv

    # The im curves
    im_list = [graded_Cvt_Erhg_list[i]*Rsd*Cv+il_list[i] for i in range(num_points)]
    Wilson_Stratified_im_list_50 = [Wilson_Stratified.stratified_head_loss(Vls, Dp, GSD[0.5], epsilon, nu, rhol, rhos, musf, Cv)
                                    for Vls in vls_list]
    Wilson_Stratified_im_list_85 = [Wilson_Stratified.stratified_head_loss(Vls, Dp, GSD[0.85], epsilon, nu, rhol, rhos, musf, Cv)
                                    for Vls in vls_list]
    Wilson_v50_im_list = [Wilson_V50.heterogeneous_head_loss(Vls, Dp, GSD[0.50], GSD[0.85], epsilon, nu, rhol, rhos, musf, Cv)
                          for Vls in vls_list]

    if plt:
        fig = plt.figure(figsize=(11, 7.5))
        # log x and y axis
        Erhg_title = "Erhg for Dp=%0.3fm, d50=%0.2fmm, D85=%0.2fmm, Rsd=%0.3f, Cv=%0.3f, rhom=%0.3f" % (Dp, d*1000,
                                                                                                        GSD[0.85]*1000,
                                                                                                        Rsd, Cv, rhom)
        Erhg_plot = fig.add_subplot(211, title=Erhg_title, xlim=(0.001, 1.0), ylim=(0.001, 2))
        Erhg_plot.loglog(il_list, il_list, linewidth=1, linestyle='--', color='blue')
        Erhg_plot.loglog(il_list, graded_Cvt_Erhg_list, linewidth=2, color='red')
        Erhg_plot.loglog(il_list, Wilson_Stratified_ERHG_list_50, linewidth=2, linestyle='--', color='brown')
        Erhg_plot.loglog(il_list, Wilson_V50_ERHG_list, linewidth=2, linestyle='dotted', color='brown')
        Erhg_plot.loglog(LDV_by_Cv_ils, LDV_by_Cv_Erhg, color='magenta', marker='^', linestyle='dotted', linewidth=1)
        Erhg_plot.loglog(LDV_by_d_ils, LDV_by_d_Erhg, color='purple', marker='^', linestyle='dotted', linewidth=1)

        Erhg_plot.grid(b=True, which='both')

        HG_title = "Hydraulic gradient for Dp=%0.3fm, d50=%0.2fmm, D85=%0.2fmm, Rsd=%0.3f, Cv=%0.3f, " \
                   "rhom=%0.3f" % (Dp, d*1000, GSD[0.85]*1000, Rsd, Cv, rhom)

        spot10 = vls_list.index(10)
        hg_ymax = max(im_list[spot10], Wilson_Stratified_im_list_85[spot10])
        HG_plot = fig.add_subplot(212, title=HG_title, xlim=(0, 10), ylim=(0, hg_ymax))
        HG_plot.plot(vls_list, il_list, linewidth=1, linestyle='--', color='blue', label="il")
        HG_plot.plot(vls_list, im_list, linewidth=2, color='red', label="DHLLDV im Graded Cvt")
        HG_plot.plot(vls_list, Wilson_Stratified_im_list_50, linewidth=2, linestyle='--', color='brown',
                     label="Wilson Sliding im D50")
        HG_plot.plot(vls_list, Wilson_v50_im_list, linewidth=2, linestyle='dotted', color='brown',
                     label="Wilson V50 im")
        HG_plot.plot(LDV_by_Cv, LDV_by_Cv_im, color='magenta', marker='^', linestyle='dotted', linewidth=1,
                     label="LDV by Cv")
        HG_plot.plot(LDV_by_d, LDV_by_d_im, color='purple', marker='^', linestyle='dotted', linewidth=1,
                     label="LDV by diameter")
        vldv = DHLLDV_framework.LDV(None, Dp, d, epsilon, nu, rhol, rhos, Cv)
        HG_plot.plot(vldv, im_ldv, color='orange', marker='o')

        HG_plot.grid(b=True, which='both')
        legend = HG_plot.legend()
        for label in legend.get_texts():
            label.set_fontsize('small')

    #     def on_plot_hover(event):
    #         for curve in Erhg_plot.get_lines():
    #             if curve.contains(event)[0]:
    #                 print "over %s" % curve.get_gid()
    #
    #     fig.canvas.mpl_connect('motion_notify_event', on_plot_hover)
        plt.tight_layout()
        plt.show()
