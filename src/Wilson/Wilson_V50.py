"""
Wilson_V50.py - Heterogenous transport using the Wilson V50 model
"""
from math import cosh, log, sqrt
from DHLLDV.heterogeneous import vt_ruby
from DHLLDV.DHLLDV_constants import gravity
from DHLLDV.homogeneous import pipe_reynolds_number, swamee_jain_ff, fluid_head_loss

def w(d, nu, rhol, rhos, musf):
    """Return w, the particle associated velocity
            d = Particle diameter (m)
            nu = fluid kinematic viscosity in m2/sec
            rhol = density of the fluid (ton/m3)
            rhos = particle density (ton/m3)
            musf = Coefficient of sliding friction
        """
    Rsd = (rhos - rhol) / rhol  # Eqn 8.2-1
    return 0.9*vt_ruby(d, Rsd, nu) + 2.7*(Rsd * gravity*musf)**(1.0/3.0)

def sigma(Dp, d50, d85, nu, rhol, rhos, musf):
    """Return sigma, the standard deviation of the particle associated velocity across
      the grain size distribution
            Dp = Pipe diameter (m)
            d50 = Median Particle diameter (m)
            d85 = Particle diameter coarser than 85% of the grains by weight
            nu = fluid kinematic viscosity in m2/sec
            rhol = density of the fluid (ton/m3)
            rhos = particle density (ton/m3)
            musf = Coefficient of sliding friction
        """
    top = w(d85, nu, rhol, rhos, musf) * cosh(60*d85/Dp)
    bottom = w(d50, nu, rhol, rhos, musf) * cosh(60*d50/Dp)
    return log(top/bottom, 10)


def M(Dp, d50, d85, nu, musf, rhol, rhos):
    """Return M, the exponent related to the grain size distribution
            Dp = Pipe diameter (m)
            d50 = Median Particle diameter (m)
            d85 = Particle diameter coarser than 85% of the grains by weight
            nu = fluid kinematic viscosity in m2/sec
            rhol = density of the fluid (ton/m3)
            rhos = particle density (ton/m3)
            musf = Coefficient of sliding friction
        """
    return (0.25 + 13 * sigma(Dp, d50, d85, nu, rhol, rhos, musf)**2)**(-0.5)

def V50(Vls, Dp, d50, d85, epsilon, nu, rhol, rhos, musf):
    """Return the V50, the velocity at which half the particles are in contact with the pipe wall
            Vls = average line speed (velocity, m/sec)
            Dp = Pipe diameter (m)
            d50 = Median Particle diameter (m)
            d85 = Particle diameter coarser than 85% of the grains by weight
            epsilon = absolute pipe roughness (m)
            nu = fluid kinematic viscosity in m2/sec
            rhol = density of the fluid (ton/m3)
            rhos = particle density (ton/m3)
            musf = Coefficient of sliding friction
        """
    w50 = w(d50, nu, rhol, rhos, musf)
    Re = pipe_reynolds_number(Vls, Dp, nu)
    lamdal = swamee_jain_ff(Re, Dp, epsilon)
    return w50 * sqrt(8/lamdal) * cosh(60*d50/Dp)

def Erhg(vls, Dp, d50, d85, epsilon, nu, rhol, rhos, musf):
    """Return the relative excess head loss using gthe Wilson V50 model
            Vls = average line speed (velocity, m/sec)
            Dp = Pipe diameter (m)
            d50 = Median Particle diameter (m)
            d85 = Particle diameter coarser than 85% of the grains by weight
            epsilon = absolute pipe roughness (m)
            nu = fluid kinematic viscosity in m2/sec
            rhol = density of the fluid (ton/m3)
            rhos = particle density (ton/m3)
            musf = The coefficient of sliding friction
        """
    _M = M(Dp, d50, d85, nu, rhol, rhos, musf)
    _V50 = V50(vls, Dp, d50, d85, epsilon, nu, rhol, rhos, musf)
    return (musf/2)*(_V50/vls)**_M

def heterogeneous_pressure_loss(vls, Dp, d50, d85, epsilon, nu, rhol, rhos, Cvs, musf):
    """Return the pressure loss (delta_pm in kPa per m) for heterogeneous flow.
       vls = average line speed (velocity, m/sec)
       Dp = Pipe diameter (m)
       d50 = Median Particle diameter (m)
       d85 = Particle diameter coarser than 85% of the grains by weight
       epsilon = absolute pipe roughness (m)
       nu = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
       Cvs = insitu volume concentration
       musf = The coefficient of sliding friction
    """
    return heterogeneous_head_loss(vls, Dp, d50, d85, epsilon, nu, rhol, rhos, Cvs, musf)*gravity*rhol


def heterogeneous_head_loss(vls, Dp, d50, d85, epsilon, nu, rhol, rhos, Cvs, musf):
    """Return the head loss (m.w.c per m) for (pseudo) heterogeneous flow.
       vls = average line speed (velocity, m/sec)
       Dp = Pipe diameter (m)
       d50 = Median Particle diameter (m)
       d85 = Particle diameter coarser than 85% of the grains by weight
       epsilon = absolute pipe roughness (m)
       nu = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
       Cvs = insitu volume concentration
       musf = The coefficient of sliding friction
    """
    il = fluid_head_loss(vls, Dp, epsilon, nu, rhol)
    Rsd = (rhos - rhol)/rhol     # Eqn 8.2-1
    return Erhg(vls, Dp, d50, d85, epsilon, nu, rhol, rhos, musf)*Rsd*Cvs + il