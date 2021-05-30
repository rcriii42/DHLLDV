'''
viewer - visualize the curves for a given sand 
Created on Oct 15, 2016

@author: rcriii
'''

import csv

from DHLLDV import DHLLDV_constants
from DHLLDV import DHLLDV_framework
from DHLLDV import homogeneous

#import numpy as np
try:
    import matplotlib.pyplot as plt
except:
    print('matplotlib not found')
    plt = None


if __name__ == '__main__':
    Dp = 0.1524  #Pipe diameter
    d = 0.2/1000.
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

    Erhg_obj_list = [DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cv, get_dict=True) for vls in vls_list]
    il_list = [Erhg_obj['il'] for Erhg_obj in Erhg_obj_list]
    print(vls_list[0], il_list[0])
    print(vls_list[-1], il_list[-1])

    #The Erhg Curves
    Erhg_list = [Erhg_obj[Erhg_obj['regime']] for Erhg_obj in Erhg_obj_list]
    #FB_Erhg_list = [Erhg_obj['FB'] for Erhg_obj in Erhg_obj_list]
    SB_Erhg_list = [Erhg_obj['SB'] for Erhg_obj in Erhg_obj_list]
    He_Erhg_list = [Erhg_obj['He'] for Erhg_obj in Erhg_obj_list]
    #Erhg for the ELM is just the il
    Ho_Erhg_list = [Erhg_obj['Ho'] for Erhg_obj in Erhg_obj_list]
    Cvt = Cv
    Cvs_from_Cvt_list = [DHLLDV_framework.Cvs_from_Cvt(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt) for vls in vls_list]
    Cvt_Erhg_list = [DHLLDV_framework.Cvt_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cv) for vls in vls_list]

    graded_Cvs_Erhg_list = [DHLLDV_framework.Erhg_graded(GSD, vls, Dp, epsilon, nu, rhol, rhos, Cv, Cvt_eq_Cvs=False)
                            for vls in vls_list]
    graded_Cvt_Erhg_list = [DHLLDV_framework.Erhg_graded(GSD, vls, Dp, epsilon, nu, rhol, rhos, Cv, Cvt_eq_Cvs=True)
                            for vls in vls_list]

    #The im curves
    im_list = [Erhg_list[i]*Rsd*Cv+il_list[i] for i in range(200)]
    #FB_im_list = [FB_Erhg_list[i]*Rsd*Cv+il_list[i] for i in range(200)]
    SB_im_list = [SB_Erhg_list[i]*Rsd*Cv+il_list[i] for i in range(200)]
    He_im_list = [He_Erhg_list[i]*Rsd*Cv+il_list[i] for i in range(200)]
    ELM_im_list = [il_list[i]*rhom for i in range(200)]
    Ho_im_list = [Ho_Erhg_list[i]*Rsd*Cv+il_list[i] for i in range(200)]
    Cvt_im_list = [Cvt_Erhg_list[i]*Rsd*Cv+il_list[i] for i in range(200)]
    graded_Cvs_im_list = [graded_Cvs_Erhg_list[i] * Rsd * Cv + il_list[i] for i in range(200)]
    graded_Cvt_im_list = [graded_Cvt_Erhg_list[i] * Rsd * Cv + il_list[i] for i in range(200)]
    
    #The LDV
    Cv_list = [(i+1)/100. for i in range(50)]
    LDV_vls_list = [DHLLDV_framework.LDV(1, Dp, d, epsilon, nu, rhol, rhos, Cv) for Cv in Cv_list]
    LDV_il_list = [homogeneous.fluid_head_loss(vls, Dp, epsilon, nu, rhol) for vls in LDV_vls_list]
    LDV_Ergh_list = [DHLLDV_framework.Cvs_Erhg(LDV_vls_list[i], Dp, d, epsilon, nu, rhol, rhos, Cv_list[i]) for i in range(50)]
    LDV_im_list = [LDV_Ergh_list[i]*Rsd*Cv_list[i]+LDV_il_list[i] for i in range(50)]
    
    regime_list = [Erhg_obj['regime'] for Erhg_obj in Erhg_obj_list ]

    erhg_file = open("eerhg.csv", 'w')

    if plt:
        fig = plt.figure(figsize=(11,7.5))
        # log x and y axis
        Erhg_title = "Erhg for Dp=%0.3fm, d=%0.1fmm, Rsd=%0.3f, Cv=%0.3f, rhom=%0.3f"%(Dp, d*1000, Rsd, Cv, rhom)
        Erhg_plot = fig.add_subplot(211, title=Erhg_title, xlim=(0.001, 1.0), ylim=(0.001, 2))
        #Erhg_plot.loglog(il_list, FB_Erhg_list, linewidth=1, linestyle='--', color='c')
        Erhg_plot.loglog(il_list, SB_Erhg_list, linewidth=3, linestyle='--', color='saddlebrown')
        Erhg_plot.loglog(il_list, il_list, linewidth=1, linestyle='--', color='blue')
        Erhg_plot.loglog(il_list, Ho_Erhg_list, linewidth=3, linestyle='--', color='brown')
        Erhg_plot.loglog(il_list, Erhg_list, linewidth=2, color='red')
        Erhg_plot.loglog(il_list, Cvt_Erhg_list, linewidth=2, linestyle='--', color='green')
        Erhg_plot.loglog(il_list, graded_Cvs_Erhg_list, linewidth=3, color='gold')
        Erhg_plot.loglog(il_list, graded_Cvt_Erhg_list, linewidth=3, linestyle='--', color='black')

        # Erhg_plot.loglog(il_list, He_Erhg_list, linewidth=1, linestyle='--', color='b')
        # Erhg_plot.loglog(il_list, Erhg_list, linewidth=2, color='r')
        Erhg_plot.grid(b=True, which='both')

        HG_title = "Hydraulic gradient for Dp=%0.3fm, d=%0.1fmm, Rsd=%0.3f, Cv=%0.3f, rhom=%0.3f"%(Dp, d*1000, Rsd, Cv, rhom)

        spot10 = vls_list.index(10)
        hg_ymax = max(SB_im_list[spot10], Cvt_im_list[spot10])
        HG_plot = fig.add_subplot(212, title=HG_title, xlim=(0,10), ylim=(0,hg_ymax))
        #HG_plot.plot(vls_list, FB_im_list, linewidth=1, linestyle='--', color='c', label="FB Cvs=c")
        HG_plot.plot(vls_list, SB_im_list, linewidth=3, linestyle='--', color='saddlebrown', label="SB Cvs=c")
        HG_plot.plot(vls_list, ELM_im_list, linewidth=1, linestyle='--', color='blue', label="ELM Cvs=c")
        HG_plot.plot(vls_list, Ho_im_list, linewidth=3, linestyle='--', color='brown', label="Ho Cvs=c")
        HG_plot.plot(vls_list, im_list, linewidth=2, color='red', label="Uniform Cvs=c")
        HG_plot.plot(vls_list, Cvt_im_list, linewidth=2, linestyle='--', color='green', label="Uniform Cvt=c")
        HG_plot.plot(vls_list, graded_Cvs_im_list, linewidth=3, color='gold', label="Graded Cvs=c")
        HG_plot.plot(vls_list, graded_Cvt_im_list, linewidth=3, linestyle='--', color='black', label="Graded Cvt=c")

        # HG_plot.plot(vls_list, He_im_list, linewidth=1, linestyle='--', color='b', label="He Cvs=c")
        # HG_plot.plot(vls_list, Ho_im_list, linewidth=2, linestyle='--', color='brown', label="Ho Cvs=c")
        # HG_plot.plot(LDV_vls_list, LDV_im_list, linewidth=1, linestyle='dotted', color='magenta', label="LDV")
        HG_plot.grid(b=True, which='both')
        legend = HG_plot.legend()
        for label in legend.get_texts():
            label.set_fontsize('small')

        # Cvs_title = "Cvs given Cvt for Dp=%0.3fm, d=%0.1fmm, Rsd=%0.3f, Cvt=%0.3f, rhom=%0.3f"%(Dp, d*1000, Rsd, Cv, rhom)
        # Cvs_plot = fig.add_subplot(313, title=Cvs_title, xlim=(0, 10), ylim=(0, 1))
        # Cvs_plot.plot(vls_list, Cvs_from_Cvt_list, linewidth=1, linestyle='--', color='c')
        # Cvs_plot.grid(True)

    #     def on_plot_hover(event):
    #         for curve in Erhg_plot.get_lines():
    #             if curve.contains(event)[0]:
    #                 print "over %s" % curve.get_gid()
    #
    #     fig.canvas.mpl_connect('motion_notify_event', on_plot_hover)
        plt.tight_layout()
        plt.show()
