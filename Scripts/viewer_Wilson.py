'''
viewer_Wilson - Compare the DHLLDV and Wilson curves for a given sand
Created on Oct 15, 2016

@author: rcriii
'''

import csv

from DHLLDV import DHLLDV_constants
from DHLLDV import DHLLDV_framework
from DHLLDV import homogeneous

from Wilson import Wilson_Stratified

#import numpy as np
try:
    import matplotlib.pyplot as plt
except:
    print('matplotlib not found')
    plt = None


if __name__ == '__main__':
    Dp = 0.1524  #Pipe diameter
    d = 2.0/1000.
    GSD = {0.15: d / 2.72,
           0.50: d,
           0.85: d * 2.72}
    epsilon = DHLLDV_constants.steel_roughness
    nu = 1.0508e-6  # DHLLDV_constants.water_viscosity[20]
    rhos = 2.65
    rhol = 1.0248103  # DHLLDV_constants.water_density[20]
    Rsd = (rhos - rhol)/rhol
    Cv = 0.175
    rhom = Cv*(rhos-rhol)+rhol
    
    vls_list = [(i+1)/10. for i in range(200)]

    #The DHLLDV model for the given material
    Erhg_obj_list = [DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cv, get_dict=True) for vls in vls_list]
    il_list = [Erhg_obj['il'] for Erhg_obj in Erhg_obj_list]
    Cvt = Cv
    Cvs_from_Cvt_list = [DHLLDV_framework.Cvs_from_Cvt(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt) for vls in vls_list]
    Cvt_Erhg_list = [DHLLDV_framework.Cvt_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cv) for vls in vls_list]
    graded_Cvt_Erhg_list = [DHLLDV_framework.Erhg_graded(GSD, vls, Dp, epsilon, nu, rhol, rhos, Cv, Cvt_eq_Cvs=True)
                            for vls in vls_list]

    #Wilson Coarse for the D50 and D85
    musf = DHLLDV_constants.musf
    Wilson_Stratified_ERHG_list_50 = [Wilson_Stratified.Erhg(Vls, Dp, GSD[0.5], epsilon, nu, rhol, rhos, musf, Cv)
                                      for Vls in vls_list]
    Wilson_Stratified_ERHG_list_85 = [Wilson_Stratified.Erhg(Vls, Dp, GSD[0.85], epsilon, nu, rhol, rhos, musf, Cv)
                                      for Vls in vls_list]


    #The im curves
    im_list = [graded_Cvt_Erhg_list[i]*Rsd*Cv+il_list[i] for i in range(200)]
    Wilson_Stratified_im_list_50 = [Wilson_Stratified.stratified_head_loss(Vls, Dp, GSD[0.5], epsilon, nu, rhol, rhos, musf, Cv)
                                    for Vls in vls_list]
    Wilson_Stratified_im_list_85 = [Wilson_Stratified.stratified_head_loss(Vls, Dp, GSD[0.85], epsilon, nu, rhol, rhos, musf, Cv)
                                    for Vls in vls_list]

    if plt:
        fig = plt.figure(figsize=(11,7.5))
        # log x and y axis
        Erhg_title = "Erhg for Dp=%0.3fm, d=%0.2fmm, Rsd=%0.3f, Cv=%0.3f, rhom=%0.3f"%(Dp, d*1000, Rsd, Cv, rhom)
        Erhg_plot = fig.add_subplot(211, title=Erhg_title, xlim=(0.001, 1.0), ylim=(0.001, 2))
        Erhg_plot.loglog(il_list, il_list, linewidth=1, linestyle='--', color='blue')
        Erhg_plot.loglog(il_list, Cvt_Erhg_list, linewidth=2, color='red')
        Erhg_plot.loglog(il_list, graded_Cvt_Erhg_list, linewidth=2, linestyle='--', color='red')
        Erhg_plot.loglog(il_list, Wilson_Stratified_ERHG_list_50, linewidth=2, linestyle='--', color='brown')
        Erhg_plot.loglog(il_list, Wilson_Stratified_ERHG_list_85, linewidth=2, linestyle='dotted', color='brown')

        Erhg_plot.grid(b=True, which='both')

        HG_title = "Hydraulic gradient for Dp=%0.3fm, d=%0.2fmm, Rsd=%0.3f, Cv=%0.3f, rhom=%0.3f"%(Dp, d*1000, Rsd, Cv, rhom)

        spot10 = vls_list.index(10)
        hg_ymax = max(im_list[spot10], Wilson_Stratified_im_list_85[spot10])
        HG_plot = fig.add_subplot(212, title=HG_title, xlim=(0,10), ylim=(0,hg_ymax))
        HG_plot.plot(vls_list, il_list, linewidth=1, linestyle='--', color='blue', label="il")
        HG_plot.plot(vls_list, im_list, linewidth=2, color='red', label="DHLLDV im Graded Cvt")
        HG_plot.plot(vls_list, Wilson_Stratified_im_list_50, linewidth=2, linestyle='--', color='brown', label="Wilson Sliding im D50")
        HG_plot.plot(vls_list, Wilson_Stratified_im_list_85, linewidth=2, linestyle='dotted', color='brown', label="Wilson Sliding im D85")

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
