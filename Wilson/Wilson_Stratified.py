"""
Wilson Stratified - Implementing the Wilson stratified model as presented in section 6.20.1
"""

from math import log

from DHLLDV.DHLLDV_constants import Cvb

def Vsm_max(Dp, d, rhol, rhos, musf):
    """Return the maximum velocity at the limit of stationary deposition

        Dp = Pipe diameter (m)
        d = Particle diameter (m)
        rhol = density of the fluid (ton/m3)
        rhos = particle density (ton/m3)
        musf = The oefficient of sliding friction
    """
    Rsd = (rhos - rhol)/rhol     # Eqn 8.2-1
    top = 8.8 * (musf * Rsd/0.66)**0.55 * Dp**0.7 * d**1.75
    bottom = d**2 + 0.11 * Dp**0.7
    return top/bottom   # Eqn. 6.20-34

def Cvr_max(Dp, d, rhol, rhos):
    """Return the relative volume concetration at Vsm_max

        Dp = Pipe diameter (m)
        d = Particle diameter (m)
        rhol = density of the fluid (ton/m3)
        rhos = particle density (ton/m3)
    """
    Rsd = (rhos - rhol) / rhol  # Eqn 8.2-1
    return 0.16*Dp**0.4 / (d**0.84 * (Rsd/1.65)**0.17)  # Eqn. 6.20-35

def Vsm(Dp, d, rhol, rhos, musf, Cv):
    """Return the maximum velocity at the limit of stationary deposition

        Dp = Pipe diameter (m)
        d = Particle diameter (m)
        rhol = density of the fluid (ton/m3)
        rhos = particle density (ton/m3)
        musf = The oefficient of sliding friction
        Cv = The volume concentration
    """
    Cvrmx = Cvr_max(Dp, d, rhol, rhos)
    Vsmx = Vsm_max(Dp, d, rhol, rhos, musf)
    Cvr = Cv/Cvb
    if Cvrmx <= 0.33:
        alpha = log(0.333)/log(Cvrmx)
        Vs = Vsmx * 6.75 * Cvr**alpha * (1 - Cvr**alpha)**2 # Eqn. 6.20-36
    else:
        beta = log(0.666)/log(1-Cvrmx)
        Vs = Vsmx * 6.75 * (1-Cvr)**2*beta * (1-(1-Cvr)**beta)  # Eqn. 6.20-36

    return min(Vs, Vsmx)
