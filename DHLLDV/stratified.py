'''
stratified.py - Calculations of fixed and sliding bed transport

Created on Oct 22, 2014

@author: RCRamsdell
'''

from math import pi, sin, log

from .DHLLDV_constants import gravity, Arel_to_beta, musf, Cvb, alpha_tel
from . import homogeneous


def beta(Cvs):
    """Return the angle beta based on the Cvs and Cvb"""
    return Arel_to_beta[Cvs/Cvb]


def perimeters(Dp, Cvs):
    """Return the four perimeters:
       Op  = The perimeter of the pipe
       O1  = The length of pipewall above the bed
       O12 = The width of the top of the bed
       O2  = The length of pipewall/bed contact
    """
    B = beta(Cvs)
    Op = pi * Dp        # Eqn 8.4-1
    O1 = (pi - B) * Dp  # Eqn 8.4-2
    O2 = Op - O1        # Eqn 8.4-3
    O12 = Dp * sin(B)   # Eqn 8.4-4
    return Op, O1, O12, O2


def areas(Dp, Cvs):
    """Return the three areas in the pipe:
       Ap = pipe area
       A1 = Area of clear fluid above the bed
       A2 = Area of bed
    """
    Arel = Cvs/Cvb
    Ap = pi*(Dp/2)**2   # Eqn 8.4-5
    A2 = Ap * Arel      # Eqn 8.4-6
    A1 = Ap - A2        # Eqn 8.4-7
    return Ap, A1, A2


def lambda1(Dp_H, v1, epsilon, nu_l):
    """Return the friction factor for the pipewall above the bed (eqn 8.4-12)
       Dp_H = Hydraulic radius of the pipe above the bed (m)
       v1 = velocity of the fluid above the bed (m/sec)
       epsilon = absolute pipe roughness (m)
       nu_l = fluid kinematic viscosity in m2/sec
    """
    Re = v1 * Dp_H/nu_l
    c1 = 0.27*epsilon/Dp_H
    c2 = 5.75/Re**0.9
    bottom = log(c1+c2)**2
    return 1.325/bottom # Eqn 8.4-12


def lambda12(Dp_H, d, v1, v2, nu_l):
    """Return the bed friction factor lambda12 (eqn 8.4-13, no sheet flow)
       Dp_H = Hydraulic radius of the pipe above the bed (m)
       d = Particle diameter (m)
       v1 = velocity of the fluid above the bed (m/sec)
       v2 = velocity of the bed (m/sec)
       nu_l = fluid kinematic viscosity in m2/sec
    """
    Re = (v1 - v2) * Dp_H/nu_l
    c1 = 0.27 * d/Dp_H
    c2 = 5.75/Re**0.9
    bottom = log(c1+c2)**2
    return 1.325*alpha_tel/bottom # Eqn 8.4-13


def lambda12_sf(Dp_H, d, v1, v2, epsilon, nu_l, rhol, rhos):
    """Return the bed friction factor lambda12 (eqn 8.4-14, with sheet flow)
       Dp = Pipe diameter (m)
       d = Particle diameter (m)
       v1 = velocity of the fluid above the bed (m/sec)
       v2 = velocity of the bed (m/sec)
       epsilon = absolute pipe roughness (m)
       nu_l = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
    """
    Rsd = (rhos - rhol)/rhol     # Eqn 8.2-1
    first = ((v1-v2)/(2*gravity*Dp_H*Rsd)**0.5)**2.73
    second = ((rhos*(pi/6)*d**3)/rhol)**0.094
    return 0.83*lambda1(Dp_H, v1, epsilon, nu_l) + 0.37*first*second    # Eqn 8.4-14


def fb_pressure_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs):
    """Return the pressure loss for fluid above a fixed bed.
       vls = average line speed (velocity, m/sec)
       Dp = Pipe diameter (m)
       d = Particle diameter (m)
       epsilon = absolute pipe roughness (m)
       nu = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
       Cvs = insitu volume concentration
    """
    Ap, A1, A2 = areas(Dp, Cvs)
    Op, O1, O12, O2 = perimeters(Dp, Cvs)
    DH1 = 4*A1/(O1 + O12)   # Eqn 8.4-8
    v1 = vls*Ap/A1          # Eqn 8.4-10 with v2 = 0
    v2 = 0.0                # Velocity of the bed
    lbd1 = lambda1(DH1, v1, epsilon, nu)
    tau1_l = lbd1*rhol*v1**2/8  # Eqn 8.4-12
    F1_l = tau1_l * O1          # Eqn 8.4-15
    lbd12 = max(lambda12(DH1, d, v1, v2, nu),   # See text after Eqn 8.4-14
                lambda12_sf(DH1, d, v1, v2, epsilon, nu, rhol, rhos))
    tau12_l = lbd12*rhol*v1**2/8    # Eqn 8.4-13 and 8.4-14
    F12_l = tau12_l * O12           # Eqn8.4-16 with deltaL = 1.0
    return (F1_l + F12_l)/A1        # Eqn 8.4-17


def fb_head_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs):
    """Return the head loss for fluid above a fixed bed.
       vls = average line speed (velocity, m/sec)
       Dp = Pipe diameter (m)
       d = Particle diameter (m)
       epsilon = absolute pipe roughness (m)
       nu = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
       Cvs = insitu volume concentration
    """
    delta_p = fb_pressure_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs)
    return delta_p /(rhol*gravity)  # Eqn 8.2-6 with deltaL = 1.0


def fb_Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs):
    """Return the ERHG for the fixed-bed case.
    """
    Rsd = (rhos - rhol)/rhol     # Eqn 8.2-1
    il = homogeneous.fluid_head_loss(vls, Dp, epsilon, nu, rhol)
    im = fb_head_loss(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs)
    return (im - il)/(Rsd * Cvs)    # Eqn 8.2-9


def Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs):
    """Return the relative excess hydraulic gradient for a sliding bed
       vls = average line speed (velocity, m/sec)
       Dp = Pipe diameter (m)
       d = Particle diameter (m)
       epsilon = absolute pipe roughness (m)
       nu = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
       Cvs = insitu volume concentration
    """
    return musf # Eqn 8.5-1


def sliding_bed_head_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, Cvb=0.6):
    """Return the head loss for sliding bed.
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
    Rsd = (rhos - rhol)/rhol     # Eqn 8.2-1
    return Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs)*Rsd*Cvs + il # Eqn 8.5-2


def sliding_bed_pressure_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs):
    """Return the pressure loss for a sliding bed.
       vls = average line speed (velocity, m/sec)
       Dp = Pipe diameter (m)
       d = Particle diameter (m)
       epsilon = absolute pipe roughness (m)
       nu = fluid kinematic viscosity in m2/sec
       rhol = density of the fluid (ton/m3)
       rhos = particle density (ton/m3)
       Cvs = insitu volume concentration
    """
    return sliding_bed_head_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs)*gravity*rhol    # Eqn 8.5-3


if __name__ == '__main__':
    pass
