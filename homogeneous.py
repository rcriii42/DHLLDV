'''
homogeneous.py - calculations of newtonian (fluid), homogeneous and pseudo-homogeneous flow.

Created on Oct 7, 2014

@author: RCRamsdell
'''

from math import log, exp
from DHLLDV_constants import gravity

Acv = 3.   #coefficient homogeneous regime, advised in section 8.7.
kvK = 0.4 #von Karman constant

def pipe_reynolds_number(vls, Dp, nu):
    """
    Return the reynolds number for the given velocity, fluid & pipe
    vls: velocity in m/sec
    Dp: pipe diameter in m
    nu: fluid kinematic viscosity in m2/sec
    """
    return vls*Dp/nu
    
def swamee_jain_ff(Re, Dp, epsilon):
    """
    Return the friction factor using the Swaamee-Jain equation.
    Re: Reynolds number
    Dp: Pipe diameter in m
    epsilon: pipe absolute roughness in m
    """
    if Re <= 2320:
        #laminar flow
        return 64. / Re
    c1 = epsilon / (3.7 * Dp)
    c2 = 5.75 / Re**0.9
    bottom = log(c1 + c2)**2
    return 1.325 / bottom  # eqn 8.7-3

def fluid_pressure_loss(vls, Dp, epsilon, nu, rhol):
    """
    Return the pressure loss (delta p in kPa) per m of pipe
    vls: line speed in m/sec
    Dp: Pipe diameter in m
    epsilon: pipe absolute roughness in m
    nu: fluid kinematic viscosity in m2/sec
    rhol: fluid density in ton/m3
    """
    Re = pipe_reynolds_number(vls, Dp, nu)
    lmbda = swamee_jain_ff(Re, Dp, epsilon)
    return lmbda*rhol*vls**2/(2*Dp)
    

def fluid_head_loss(vls, Dp, epsilon, nu, rhol):
    """
    Return the head loss (il in m.l.c) per m of pipe
    vls: line speed in m/sec
    Dp: Pipe diameter in m
    epsilon: pipe absolute roughness in m
    nu: fluid kinematic viscosity in m2/sec
    rhol: fluid density in ton/m3
    """
    Re = pipe_reynolds_number(vls, Dp, nu)
    lmbda = swamee_jain_ff(Re, Dp, epsilon)
    return lmbda*vls**2/(2*gravity*Dp)

def relative_viscosity(Cvs):
    """
    Return the relative viscosity (nu-m/nu-l) of a pseudo-homogeneous slurry, using the 
    Thomas (1965) approach.
    Cvs is the volume concentration of fines. 
    """
    return 1 + 2.5*Cvs + 10.05*Cvs**2 + 0.00273*exp(16.6*Cvs)  # eqn 8.15-2

def Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs):
    """Return the Erhg value for homogeneous flow.
    Use the Talmon (2013) correction for slurry density.
    vls: line speed in m/sec
    Dp: Pipe diameter in m
    d: Particle diameter in m (not used, here for consistency)
    epsilon: pipe absolute roughness in m
    nu: fluid kinematic viscosity in m2/sec
    rhol: fluid density in ton/m3
    Cvs - spatial (insitu) volume concentration of solids
    """
    Re = pipe_reynolds_number(vls, Dp, nu)
    lambda1 = swamee_jain_ff(Re, Dp, epsilon)
    Rsd = (rhos-rhol)/rhol
    rhom = rhol+Cvs*(rhos-rhol)
    deltav_to_d = min((11.6*nu)/((lambda1/8)**0.5*vls*d), 1)    #eqn 8.7-7
    
    sb = ((Acv/kvK)*log(rhom/rhol)*(lambda1/8)**0.5+1)**2
    top = 1+Rsd*Cvs - sb
    bottom = Rsd*Cvs*sb
    il = fluid_head_loss(vls, Dp, epsilon, nu, rhol)
    return il*(1-(1-top/bottom)*(1-deltav_to_d))                    #eqn 8.7-8

def homogeneous_pressure_loss(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs):
    """
    Return the pressure loss (delta_pm in kPa per m) for (pseudo) homogeneous flow incorporating viscosity correction.
    vls: line speed in m/sec
    Dp: Pipe diameter in m
    epsilon: pipe absolute roughness in m
    nu: fluid kinematic viscosity in m2/sec
    rhol: fluid density in ton/m3
    Cvs - spatial (insitu) volume concentration of solids
    """
    return homogeneous_head_loss(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)*gravity/rhol

def homogeneous_head_loss(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs):
    """
    Return the head loss (m.l.c per m) for (pseudo) homogeneous flow incorporating viscosity correction.
    vls: line speed in m/sec
    Dp: Pipe diameter in m
    epsilon: pipe absolute roughness in m
    nu: fluid kinematic viscosity in m2/sec
    rhol: fluid density in ton/m3
    Cvs - spatial (insitu) volume concentration of solids
    """
    il = fluid_head_loss(vls, Dp, epsilon, nu, rhol)
    Rsd = (rhos-rhol)/rhol
    return Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)*Rsd*Cvs + il