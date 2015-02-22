'''
heterogeneous.py - heterogeneous transport model.
Created on Feb 21, 2015

@author: rcriii
'''
from DHLLDV_constants import gravity, Arel_to_beta
import homogeneous
from math import pi, sin, log

def vt_grace(d, Rsd, nu):
    """vt_grace - terminal settling velocity via the Grace method (equations 4.4-21 - 4.4-27)
    """
    d_mm = d*1000.
    Dstar = d_mm*(Rsd*gravity/nu^2)**(1./3.)
    if Dstar < 3.8:
        vtstar = Dstar**2/18. - 3.1234e-04*Dstar**5. + 1.6415e-06*Dstar**8. - 7.278e-10*Dstar**11
    elif 3.8 <= Dstar < 7.58:
        vtstar =10**(-1.5446 + 2.9162*log(Dstar) - 1.0432*log(Dstar)**2)
    elif 7.58 <= Dstar < 227:
        vtstar = 10**(-1.64758 + 2.94786*log(Dstar) - 1.09703*log(Dstar)**2 + 0.17129*log(Dstar)**3)
    else: #227 <= Dstar < 3500
        vtstar = 10**(5.1837 - 4.51034*log(Dstar) + 1.687*log(Dstar)**2 - 0.189135*log(Dstar)**3)
    vt_mmsec = vtstar * (1/(nu*Rsd*gravity)**(-1./3.))
    return vt_mmsec/1000.

def Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs):
    """Relative excess pressure gadient, per equation 8.5-2
       vls = average line speed (velocity, m/sec)
       Dp = Pipe diameter (m)
       d = Particle diameter (m)
       epsilon = absolute pipe roughness (m)
       nu = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
       Cvs = insitu volume concentration
    """
    Rsd = (rhos-rhol)/rhol
    vt = vt_grace(d, Rsd, nu)
    Rep = vt*d/nu  #eqn 4.2-6
    top = 4.7 + 0.41*Rep**0.75
    bottom = 1 + 0.175*Rep**0.75
    beta = top/bottom  #eqn 4.6-4
    KC = 0.175*(1+beta)
    Shr = vt*(1-Cvs/KC)**beta  #Eqn 8.5-2
    
    Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
    lbdl = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
    Srs = 7.5**2 * (1/lbdl) * (vt/(gravity*d)**0.5)**(8./3.) * ((nu*gravity)**(1./3.)/vls)**2  #Eqn 8.5-2
    return Shr + Srs

def 
if __name__ == '__main__':
    pass