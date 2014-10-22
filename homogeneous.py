'''
homogeneous.py - calculations of newtonian (fluid), homogeneous and pseudo-homogeneous flow.

Created on Oct 7, 2014

@author: RCRamsdell
'''

from math import log, exp
from DHLLDV_constants import gravity

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
        return 64./Re
    c1 = epsilon/(3.7*Dp)
    c2 = 5.75/Re**0.9
    bottom = log(c1+c2)**2
    return 1.325/bottom

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
    Return the head loss (il in m.w.c) per m of pipe
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
    Thomas (21965) approach.
    Cvs is the volume concentration of fines. 
    """
    return 1 + 2.5*Cvs + 10.05*Cvs**2 + 0.00273*exp(16.6*Cvs)

def homogeneous_pressure_loss(vls, Dp, epsilon, nu, rhol, Cvs):
    """
    Return the pressure loss (delta_pm in kPa per m) for (pseudo) homogeneous flow incorporating viscosity correction.
    vls: line speed in m/sec
    Dp: Pipe diameter in m
    epsilon: pipe absolute roughness in m
    nu: fluid kinematic viscosity in m2/sec
    rhol: fluid density in ton/m3
    Cvs - in situ volume concentration of solids
    """
    nu_m = relative_viscosity(Cvs)*nu
    return fluid_pressure_loss(vls, Dp, epsilon, nu_m, rhol)

def homogeneous_head_loss(vls, Dp, epsilon, nu, rhol, Cvs):
    """
    Return the head loss (m.w.c per m) for (pseudo) homogeneous flow incorporating viscosity correction.
    vls: line speed in m/sec
    Dp: Pipe diameter in m
    epsilon: pipe absolute roughness in m
    nu: fluid kinematic viscosity in m2/sec
    rhol: fluid density in ton/m3
    Cvs - in situ volume concentration of solids
    """
    nu_m = relative_viscosity(Cvs)*nu
    return fluid_head_loss(vls, Dp, epsilon, nu_m, rhol)