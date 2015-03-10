'''
Created on Mar 3, 2015

@author: rcriii
'''

import stratified
import heterogeneous
import homogeneous
from DHLLDV_constants import gravity
from math import pi, exp


def Cvs_Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, get_dict=False):
    """
    Cvs_Erhg - Calculate the Erhg for the given slurry, using the appropriate model
    vls = average line speed (velocity, m/sec)
    Dp = Pipe diameter (m)
    d = Particle diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cvs = insitu volume concentration
    get_dict: if true return the dict with all models.
    """
    Erhg_obj={'FB':stratified.fb_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
              'SB':   stratified.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
              'He':heterogeneous.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
              'Ho':  homogeneous.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
              }
    
    
    if Erhg_obj['FB'] < Erhg_obj['SB']:
        regime = 'FB'
    else:
        regime = 'SB'
    
    if Erhg_obj[regime] > Erhg_obj['He']:
        regime = 'He'
    
    if Erhg_obj[regime] < Erhg_obj['Ho']:
        regime = 'Ho'
    
    Erhg_obj['regime'] = regime
    
    if get_dict:
        return Erhg_obj
    else:
        return Erhg_obj[Erhg_obj['regime']]


def Cvs_regime(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs):
    """
    Return the name of the regime for the given slurry and velocity
    vls = average line speed (velocity, m/sec)
    Dp = Pipe diameter (m)
    d = Particle diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cvs = insitu volume concentration
    """
    Erhg_obj = Cvs_Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, get_dict=True)
    return {'FB': 'fixed bed',
            'SB': 'sliding bed',
            'He': 'heterogeneous',
            'Ho': 'homogeneous',
            }[Erhg_obj['regime']]
            
            
def LDV(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, max_steps=10):
    """
    Return the LDV for the given slurry.
    Dp = Pipe diameter (m)
    d = Particle diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cvs = insitu volume concentration
    """
    Rsd = (rhos-rhol)/rhol
    fbot = (2*gravity*Rsd*Dp)**0.5
    
    vls = 1.0
    Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
    lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
    FL_vs = 1.4*(nu*Rsd*gravity)**(1./3.)*(8/lambdal)**0.5/fbot #eqn 8.11-1
    vlsldv = FL_vs*fbot
    steps = 0
    while not (1.00001 >= vls/vlsldv > 0.99999) and steps < max_steps:
        vls = (vls + vlsldv)/2
        Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
        lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
        FL_vs = 1.4*(nu*Rsd*gravity)**(1./3.)*(8/lambdal)**0.5/fbot #eqn 8.11-1
        vlsldv = FL_vs*fbot
        steps += 1
    
    #print "VLS - lambdal_vs = %0.6f"%lambdal
    #print "VLS - FL_vs = %0.6f"%FL_vs
    
    vls = 4.5
    Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
    lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
    alphap = 3.5 * (1.65/Rsd)**(1./9)
    vt = heterogeneous.vt_grace(d, Rsd, nu)
    Rep = vt*d/nu  #eqn 4.2-6
    top = 4.7 + 0.41*Rep**0.75
    bottom = 1. + 0.175*Rep**0.75
    beta = top/bottom  #eqn 4.6-4
    KC = 0.175*(1+beta)
    FL_ss = alphap * (vt*Cvs*(1-Cvs/KC)**beta/(lambdal*fbot))**(1./3) #eqn 8.11-3
    vlsldv = FL_ss*fbot
    steps = 0
    while not (1.00001 >= vls/vlsldv > 0.99999) and steps < max_steps:
        vls = (vls + vlsldv)/2
        Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
        lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
        FL_ss = alphap * (vt*Cvs*(1-Cvs/KC)**beta/(lambdal*fbot))**(1./3) #eqn 8.11-3
        vlsldv = FL_ss*fbot
        steps += 1
#     print "VLS - vt = %0.6f"%vt
#     print "VLS - beta = %0.6f"%beta
#     print "VLS - lambdal_ss = %0.6f"%lambdal
#    print "VLS - FL_ss = %0.6f"%FL_ss
    
    FL_s = max(FL_vs, FL_ss)
    #print "VLS - FL_s = %0.6f"%FL_s
    
    vls=4.5
    if d <= 0.015*Dp:
        Cvr_ldv = 0.0039/(2*gravity*Rsd*Dp) #Eqn 8.11-7
    else:
        Cvr_ldv = 0.0318*(d/Dp)**0.5/(2*gravity*Rsd*Dp) #Eqn 8.11-7
    FL_r = alphap*((1-Cvs/KC)**beta * Cvs * (stratified.musf*stratified.Cvb*pi/8)**0.5 * Cvr_ldv**0.5/lambdal)**(1./3) #Eqn 8.11-6
    vlsldv = FL_r*fbot
    steps = 0
    while not (1.00001 >= vls/vlsldv > 0.99999) and steps < max_steps:
        vls = (vls + vlsldv)/2
        Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
        lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
        FL_r = alphap*((1-Cvs/KC)**beta * Cvs * (stratified.musf*stratified.Cvb*pi/8)**0.5 * Cvr_ldv**0.5/lambdal)**(1./3) #Eqn 8.11-6
        vlsldv = FL_r*fbot
        steps += 1
    #print "VLS - FL_r = %0.6f"%FL_r
    
    d0 = 0.00042*(1.65/Rsd)**0.5
    drough = 2./1000 #note: only valid for sand with Rsd=1.65
    if d > drough:
        FL_ul = FL_r
    elif FL_s <= FL_r:
        FL_ul = FL_s
    else:
        FL_ul = FL_s*exp(-1*d/d0) + FL_r*(1-exp(-1*d/d0))   #Eqn 8.11-8
    #print "VLS - FL_ul = %0.6f"%FL_ul
    
    vls = 2.0
    Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
    lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
    A = -1
    B = vt*(1-Cvs/KC)**beta/stratified.musf
    C = ((7.5**2/lambdal)*(vt/(gravity*d)**0.5)**(8./3)*(nu*gravity)**(2./3))/stratified.musf
    vlsldv = (-1*B - (B**2-4*A*C)**0.5)/(2*A)   #Eqn 8.11-11
    steps = 0
    while not (1.00001 >= vls/vlsldv > 0.99999) and steps < max_steps:
        vls = (vls + vlsldv)/2
        Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
        lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
        A = -1
        B = vt*(1-Cvs/KC)**beta/stratified.musf
        C = ((7.5**2/lambdal)*(vt/(gravity*d)**0.5)**(8./3)*(nu*gravity)**(2./3))/stratified.musf
        vlsldv = (-1*B - (B**2-4*A*C)**0.5)/(2*A)   #Eqn 8.11-11
        steps += 1
    FL_ll = vlsldv/fbot #Eqn 8.11-12
#     print "VLS - vt = %0.6f"%vt
#     print "VLS - A = %0.6f"%A
#     print "VLS - B = %0.6f"%B
#     print "VLS - C = %0.6f"%C
#     print "VLS - vlsldv = %0.6f"%vlsldv
#     print "VLS - FL_ll = %0.6f"%FL_ll
    
    FL = max(FL_ul, FL_ll)  #Eqn 8.11-13
#     print "VLS - FL = %0.6f"%FL
    return FL*fbot
    


if __name__ == '__main__':
    pass
