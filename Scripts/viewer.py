"""
viewer - visualize the curves for a given sand
Created on Oct 15, 2016

@author: rcriii
"""

import csv

from DHLLDV import DHLLDV_constants
from DHLLDV import SlurryObj

try:
    import matplotlib.pyplot as plt
except:
    print('matplotlib not found')
    plt = None




if __name__ == '__main__':
    S = SlurryObj.Slurry()
    S.Dp = 0.750  #Pipe diameter
    S.D50 = 0.2/1000.
    S.silt = None
    S.generate_GSD(2.72, 2.72)
    S.rhos = 2.65
    S.epsilon = DHLLDV_constants.steel_roughness
    S.fluid = 'salt'

    S.Cv = 0.24

    vls_list = [(i+1)/10. for i in range(200)]

    Erhg_curves = S.generate_Erhg_curves()
    im_curves = S.generate_im_curves()
    LDV_curves = S.generate_LDV_curves(S.D50)
    il_list = Erhg_curves['il']

    #The im curves
    im_list = im_curves['Cvs_im']
    #FB_im_list = [FB_Erhg_list[i]*Rsd*Cv+il_list[i] for i in range(200)]
    SB_im_list = im_curves['SB']
    He_im_list = im_curves['He']
    ELM_im_list = im_curves['ELM']
    Ho_im_list = im_curves['Ho']
    Cvt_im_list = im_curves['Cvt_im']
    graded_Cvs_im_list = im_curves['graded_Cvs_im']
    graded_Cvt_im_list = im_curves['graded_Cvt_im']
    
    #The LDV
    Cv_list = LDV_curves['Cv']
    LDV_vls_list = LDV_curves['vls']
    LDV_il_list = LDV_curves['il']
    LDV_Ergh_list = LDV_curves['Erhg']
    LDV_im_list = LDV_curves['im']
    
    #regime_list = [Erhg_obj['regime'] for Erhg_obj in Erhg_curves'Erhg_objects'] ]

    erhg_file = open("eerhg.csv", 'w')

    if plt:
        fig = plt.figure(figsize=(11,7.5))
        # log x and y axis
        Erhg_title = "Erhg for Dp=%0.3fm, d=%0.2fmm, Rsd=%0.3f, Cv=%0.3f, rhom=%0.3f"%(S.Dp, S.D50*1000, S.Rsd, S.Cv, S.rhom)
        Erhg_plot = fig.add_subplot(211, title=Erhg_title, xlim=(0.001, 1.0), ylim=(0.001, 2))
        #Erhg_plot.loglog(il_list, FB_Erhg_list, linewidth=1, linestyle='--', color='c')
        Erhg_plot.loglog(il_list, Erhg_curves['SB'], linewidth=3, linestyle='--', color='saddlebrown')
        Erhg_plot.loglog(il_list, il_list, linewidth=1, linestyle='--', color='blue')
        Erhg_plot.loglog(il_list, Erhg_curves['Ho'], linewidth=3, linestyle='--', color='brown')
        Erhg_plot.loglog(il_list, Erhg_curves['Cvs_Erhg'], linewidth=2, color='red')
        Erhg_plot.loglog(il_list, Erhg_curves['Cvt_Erhg'], linewidth=2, linestyle='--', color='green')
        Erhg_plot.loglog(il_list, Erhg_curves['graded_Cvs_Erhg'], linewidth=3, color='gold')
        Erhg_plot.loglog(il_list, Erhg_curves['graded_Cvt_Erhg'], linewidth=3, linestyle='--', color='black')

        # Erhg_plot.loglog(il_list, He_Erhg_list, linewidth=1, linestyle='--', color='b')
        # Erhg_plot.loglog(il_list, Erhg_list, linewidth=2, color='r')
        Erhg_plot.grid(b=True, which='both')

        HG_title = "Hydraulic gradient for Dp=%0.3fm, d=%0.2fmm, Rsd=%0.3f, Cv=%0.3f, rhom=%0.3f"%(S.Dp, S.D50*1000, S.Rsd, S.Cv, S.rhom)

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
