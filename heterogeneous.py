'''
heterogeneous.py - heterogeneous transport model.
Created on Feb 21, 2015

@author: rcriii
'''
from DHLLDV_constants import gravity, Arel_to_beta, musf, particle_ratio
import homogeneous
import stratified
from math import pi, sin, log, cosh

def vt_ruby(d, Rsd, nu, K=0.26):
    """vt_ruby - terminal settling velocity via the Ruby & Zanke formula (eqn 8.2-2)
       d particle diameter (m)
       Rsd relative solids density
       nu fluid kinematic viscosity in m2/sec
       k particle shape factor (sand = 0.26) (not used, included for compatibility
    """
    right = 10*nu/d
    left = (1+(Rsd*gravity*d**3)/(100*nu**2))**0.5 -1
    return right * left #Eqn 8.2-2


def Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, use_sf = True):
    """Relative excess pressure gradient, per equation 8.5-2
       vls = average line speed (velocity, m/sec)
       Dp = Pipe diameter (m)
       d = Particle diameter (m)
       epsilon = absolute pipe roughness (m)
       nu = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
       Cvs = insitu volume concentration
       use_sf: Whether to apply the sliding flow correction
    """
    Rsd = (rhos-rhol)/rhol
    vt = vt_ruby(d, Rsd, nu)
    Rep = vt*d/nu  #eqn 8.2-4
    top = 4.7 + 0.41*Rep**0.75
    bottom = 1. + 0.175*Rep**0.75
    beta = top/bottom  #eqn 8.2-4
    KC = 0.175*(1+beta)
    Shr = vt*(1-Cvs/KC)**beta /vls #Eqn 8.5-2
    
    Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
    lbdl = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
    Srs = 8.5**2 * (1/lbdl) * (vt/(gravity*d)**0.5)**(10./3.) * ((nu*gravity)**(1./3.)/vls)**2  #Eqn 8.5-2
    f = d/(particle_ratio * Dp)  #eqn 8.8-4
    if not use_sf or f<1:
        return Shr + Srs
    else:
        #Sliding flow per equation 8.8-5
        return (Shr + Srs + (f-1)*musf)/f

def heterogeneous_pressure_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, use_sf = True):
    """Return the pressure loss (delta_pm in kPa per m) for heterogeneous flow.
       vls = average line speed (velocity, m/sec)
       Dp = Pipe diameter (m)
       d = Particle diameter (m)
       epsilon = absolute pipe roughness (m)
       nu = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
       Cvs = insitu volume concentration
    """
    return heterogeneous_head_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, use_sf)*gravity/rhol

def heterogeneous_head_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, use_sf = True):
    """Return the head loss (m.w.c per m) for (pseudo) heterogeneous flow.
       vls = average line speed (velocity, m/sec)
       Dp = Pipe diameter (m)
       d = Particle diameter (m)
       epsilon = absolute pipe roughness (m)
       nu = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
       Cvs = insitu volume concentration
    """
    il = homogeneous.fluid_head_loss(vls, Dp, epsilon, nu, rhol)
    Rsd = (rhos-rhol)/rhol
    return Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, use_sf)*Rsd*Cvs + il

if __name__ == '__main__':
    pass