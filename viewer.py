'''
viewer - visualize the curves for a given sand 
Created on Oct 15, 2016

@author: rcriii
'''
import DHLLDV_constants
import DHLLDV_framework
import homogeneous

#import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    
    Dp = 0.762
    d = .3/1000
    epsilon = DHLLDV_constants.steel_roughness
    nu = DHLLDV_constants.water_viscosity[20] 
    rhos = 2.65
    rhol = DHLLDV_constants.water_density[20]
    Rsd = (rhos - rhol)/rhol
    Cvs = 0.1
    rhom = Cvs*(rhos-rhol)+rhol
    
    vls_list = [(i+1)/10. for i in range(200)]
    il_list = [homogeneous.fluid_head_loss(vls, Dp, epsilon, nu, rhol) for vls in vls_list]
    Erhg_obj_list = [DHLLDV_framework.Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, get_dict=True) for vls in vls_list]
    
    #The Erhg Curves
    Erhg_list = [Erhg_obj[Erhg_obj['regime']] for Erhg_obj in Erhg_obj_list]
    FB_Erhg_list = [Erhg_obj['FB'] for Erhg_obj in Erhg_obj_list]
    SB_Erhg_list = [Erhg_obj['SB'] for Erhg_obj in Erhg_obj_list]
    He_Erhg_list = [Erhg_obj['He'] for Erhg_obj in Erhg_obj_list]
    #Erhg for the ELM is just the il
    Ho_Erhg_list = [Erhg_obj['Ho'] for Erhg_obj in Erhg_obj_list]
    Cvt = Cvs
    Cvt_Erhg_list = [DHLLDV_framework.Cvt_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt) for vls in vls_list]
    
    #The im curves
    im_list = [Erhg_list[i]*Rsd*Cvs+il_list[i] for i in range(200)]
    FB_im_list = [FB_Erhg_list[i]*Rsd*Cvs+il_list[i] for i in range(200)]
    SB_im_list = [SB_Erhg_list[i]*Rsd*Cvs+il_list[i] for i in range(200)]
    He_im_list = [He_Erhg_list[i]*Rsd*Cvs+il_list[i] for i in range(200)]
    ELM_im_list = [il_list[i]*rhom for i in range(200)]
    Ho_im_list = [Ho_Erhg_list[i]*Rsd*Cvs+il_list[i] for i in range(200)]
    Cvt_im_list = [Cvt_Erhg_list[i]*Rsd*Cvt+il_list[i] for i in range(200)]
    
    #The LDV
    Cv_list = [(i+1)/100. for i in range(50)]
    LDV_vls_list = [DHLLDV_framework.LDV(1, Dp, d, epsilon, nu, rhol, rhos, Cv) for Cv in Cv_list]
    LDV_il_list = [homogeneous.fluid_head_loss(vls, Dp, epsilon, nu, rhol) for vls in LDV_vls_list]
    LDV_Ergh_list = [DHLLDV_framework.Cvs_Erhg(LDV_vls_list[i], Dp, d, epsilon, nu, rhol, rhos, Cv_list[i]) for i in range(50)]
    LDV_im_list = [LDV_Ergh_list[i]*Rsd*Cv_list[i]+LDV_il_list[i] for i in range(50)]
    
    regime_list = [Erhg_obj['regime'] for Erhg_obj in Erhg_obj_list ]
    
    fig = plt.figure()
    # log x and y axis
    Erhg_title = "Erhg for Dp=%0.3fm, d=%0.1fmm, Rsd=%0.3f, Cv=%0.3f, rhom=%0.3f"%(Dp, d*1000, Rsd, Cvs, rhom)
    Erhg_plot = fig.add_subplot(211, title=Erhg_title, xlim=(.001, 1.0), ylim=(0.001, 3))
    Erhg_plot.loglog(il_list, FB_Erhg_list, linewidth=1, linestyle='--', color='c', label="FB Cvs=c")
    Erhg_plot.loglog(il_list, SB_Erhg_list, linewidth=1, linestyle='--', color='brown', label="SB Cvs=c")
    Erhg_plot.loglog(il_list, He_Erhg_list, linewidth=1, linestyle='--', color='b', label="He Cvs=c")
    Erhg_plot.loglog(il_list, il_list, linewidth=1, linestyle='dotted', color='b', label="ELM Cvs=c")
    Erhg_plot.loglog(il_list, Ho_Erhg_list, linewidth=2, linestyle='--', color='brown', label="Ho Cvs=c")
    Erhg_plot.loglog(il_list, Erhg_list, linewidth=2, color='r', label="Resulting Cvs=c")
    Erhg_plot.loglog(il_list, Cvt_Erhg_list, linewidth=2, linestyle='--', color='g', label="Resulting Cvt=c")
    Erhg_plot.grid(True)
    legend = Erhg_plot.legend()
    for label in legend.get_texts():
        label.set_fontsize('small')
    
    
    HG_title = "Hydraulic gradient for Dp=%0.3fm, d=%0.1fmm, Rsd=%0.3f, Cv=%0.3f, rhom=%0.3f"%(Dp, d*1000, Rsd, Cvs, rhom)
    HG_plot = fig.add_subplot(212, title=HG_title, xlim=(0,10), ylim=(0,0.5))
    HG_plot.plot(vls_list, FB_im_list, linewidth=1, linestyle='--', color='c')
    HG_plot.plot(vls_list, SB_im_list, linewidth=1, linestyle='--', color='brown')
    HG_plot.plot(vls_list, He_im_list, linewidth=1, linestyle='--', color='b')
    HG_plot.plot(vls_list, ELM_im_list, linewidth=1, linestyle='dotted', color='b')
    HG_plot.plot(vls_list, Ho_im_list, linewidth=2, linestyle='--', color='brown')
    HG_plot.plot(vls_list, im_list, linewidth=2.5, color='r')
    HG_plot.plot(LDV_vls_list, LDV_im_list, linewidth=1, linestyle='dotted', color='r')
    HG_plot.plot(vls_list, Cvt_im_list, linewidth=2, linestyle='--', color='g')
    HG_plot.grid(True)
    
#     def on_plot_hover(event):
#         for curve in Erhg_plot.get_lines():
#             if curve.contains(event)[0]:
#                 print "over %s" % curve.get_gid()
#     
#     fig.canvas.mpl_connect('motion_notify_event', on_plot_hover)
    plt.show()