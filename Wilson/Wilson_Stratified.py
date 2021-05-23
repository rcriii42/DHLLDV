"""
Wilson Stratified - Implementing the Wilson stratified model as presented in section 6.20.1
"""

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