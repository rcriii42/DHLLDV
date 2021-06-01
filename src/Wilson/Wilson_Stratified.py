"""
Wilson Stratified - Implementing the Wilson stratified model as presented in section 6.20.1
"""

from math import log

from DHLLDV.homogeneous import fluid_head_loss, swamee_jain_ff, pipe_reynolds_number
from DHLLDV.DHLLDV_constants import gravity

def Vsm_max(Dp, d, rhol, rhos, musf=0.4, f=None):
    """Return the maximum velocity at the limit of stationary deposition
        Dp = Pipe diameter (m)
        d = Particle diameter (m)
        rhol = density of the fluid (ton/m3)
        rhos = particle density (ton/m3)
        musf = The coefficient of sliding friction, the default value of 0.4 is that used
               by Wilson et al.
        f =The friction factor, if given use WASC2 Eqn 5.1
    """
    d_mm = d*1000.
    Rsd = (rhos - rhol)/rhol     # Eqn 8.2-1
    top = 8.8 * (musf * Rsd/0.66)**0.55 * Dp**0.7 * d_mm**1.75
    bottom = d_mm**2 + 0.11 * Dp**0.7

    if f:
        alt = (0.018/f)**0.13 * (2 * gravity*Dp*(rhos-rhol))**0.5
        return min(alt, top/bottom)
    else:
        return top/bottom   # Eqn. 6.20-34

def Cvr_max(Dp, d, rhol, rhos):
    """Return the relative volume concentration at Vsm_max

        Dp = Pipe diameter (m)
        d = Particle diameter (m)
        rhol = density of the fluid (ton/m3)
        rhos = particle density (ton/m3)
    """
    d_mm = d*1000.0
    Rsd = (rhos - rhol) / rhol  # Eqn 8.2-1
    Cvrmx = 0.16*Dp**0.4 * d_mm**-0.84 * (Rsd/1.65)**-0.17  # Eqn. 6.20-35
    return min(0.66, max(0.05, Cvrmx))

def Vsm(Dp, d, rhol, rhos, musf, Cv, Cvb=0.6, f=None):
    """Return the velocity at the limit of stationary deposition
        Dp = Pipe diameter (m)
        d = Particle diameter (m)
        rhol = density of the fluid (ton/m3)
        rhos = particle density (ton/m3)
        musf = The oefficient of sliding friction
        Cv = The volume concentration
        Cvb = The bed concentration
        f =The friction factor, if given use WASC2 Eqn 5.1
    """
    Cvrmx = Cvr_max(Dp, d, rhol, rhos)
    Vsmx = Vsm_max(Dp, d, rhol, rhos, musf, f=f)
    Cvr = Cv/Cvb
    if Cvrmx <= 0.33:
        alpha = log(0.333)/log(Cvrmx)
        Vs = Vsmx * 6.75 * (Cvr**alpha) * (1 - Cvr**alpha)**2 # Eqn. 6.20-36
    else:
        beta = log(0.666)/log(1-Cvrmx)
        Vs = Vsmx * 6.75 * (1-Cvr)**2*beta * (1-(1-Cvr)**beta)  # Eqn. 6.20-36

    return min(Vs, Vsmx)

def Erhg(Vls, Dp, d, epsilon, nu, rhol, rhos, musf, Cvt, Cvb=0.6):
    """Return the relative excess head loss
       Assume that Eqn. 6.20-41 is calibrated for musf=0.4, and adjust accordingly
            Vls = average line speed (velocity, m/sec)
            Dp = Pipe diameter (m)
            d = Particle diameter (m)
            epsilon = absolute pipe roughness (m)
            nu = fluid kinematic viscosity in m2/sec
            rhol = density of the fluid (ton/m3)
            rhos = particle density (ton/m3)
            musf = The oefficient of sliding friction
            Cv = The delivered volume concentration
        """
    Re = pipe_reynolds_number(Vls, Dp, nu)
    f = swamee_jain_ff(Re, Dp, epsilon)
    return musf/0.4 * (0.55*Vsm(Dp, d, rhol, rhos, musf, Cvt, f=f)/Vls)**0.25 # Eqn. 6.20-41 modified for musf

def stratified_head_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, musf, Cvt, Cvb=0.6):
    """Return the head loss for the Wilson stratified (sliding bed) case
       Assume that Eqn. 6.20-41 is calibrated for musf=0.4, and adjust accordingly
            Vls = average line speed (velocity, m/sec)
            Dp = Pipe diameter (m)
            d = Particle diameter (m)
            epsilon = absolute pipe roughness (m)
            nu = fluid kinematic viscosity in m2/sec
            rhol = density of the fluid (ton/m3)
            rhos = particle density (ton/m3)
            musf = The oefficient of sliding friction
            Cvt = The delivered volume concentration
        """
    Rsd = (rhos - rhol) / rhol  # Eqn 8.2-1
    il = fluid_head_loss(vls, Dp, epsilon, nu, rhol)
    return il + Rsd*Cvt * Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, musf, Cvt, Cvb)
