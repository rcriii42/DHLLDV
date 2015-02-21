'''
stratified.py - Calculations of fixed and sliding bed transport

Created on Oct 22, 2014

@author: RCRamsdell
'''

from DHLLDV_constants import gravity, Arel_to_beta
from homogeneous import fluid_head_loss
from math import pi, sin, log


def beta(Cvs, Cvb=0.6):
    """Return the angle beta based on the Cvs and Cvb"""
    return Arel_to_beta[Cvs/Cvb]


def areas(Dp, Cvs, Cvb=0.6):
    """Return the three areas in the pipe:
       Ap = pipe area
       A1 = Area of clear fluid above the bed
       A2 = Area of bed
    """
    Arel = Cvs/Cvb
    Ap = pi*(Dp/2)**2
    A2 = Ap * Arel
    A1 = Ap - A2
    return Ap, A1, A2


def perimeters(Dp, Cvs, Cvb=0.6):
    """Return the four perimeters:
       Op  = The perimeter of the pipe
       O1  = The length of pipewall above the bed
       O12 = The width of the top of the bed
       O2  = The length of pipewall/bed contact
    """
    B = beta(Cvs, Cvb)
    Op = pi * Dp
    O1 = (pi - B) * Dp
    O12 = Dp * sin(B)
    O2 = Op - O1
    return Op, O1, O12, O2


def lambda1(Dp_H, v1, epsilon, nu_l):
    """Return the friction factor for the pipewall above the bed (eqn 8.3-12)
       Dp_H = Hydraulic radius of the pipe above the bed (m)
       v1 = velocity of the fluid above the bed (m/sec)
       epsilon = absolute pipe roughness (m)
       nu_l = fluid kinematic viscosity in m2/sec
    """
    Re = v1 * Dp_H/nu_l
    c1 = 0.27*epsilon/Dp_H
    c2 = 5.75/Re**0.9
    bottom = log(c1+c2)**2
    return 1.325/bottom


def lambda12(Dp_H, d, v1, v2, nu_l):
    """Return the bed friction factor lambda12 (eqn 8.3-13, no sheet flow)
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
    return 1.325/bottom


def lambda12_sf(Dp_H, d, v1, v2, epsilon, nu_l, rho_l, rho_s):
    """Return the bed friction factor lambda12 (eqn 8.3-14, with sheet flow)
       Dp = Pipe diameter (m)
       d = Particle diameter (m)
       v1 = velocity of the fluid above the bed (m/sec)
       v2 = velocity of the bed (m/sec)
       epsilon = absolute pipe roughness (m)
       nu_l = fluid kinematic viscosity in m2/sec
       rho_l = density of the fluid (ton/m3)
       rho_s = particle density (ton/m3)
    """
    Rsd = (rho_s - rho_l)/rho_l
    first = ((v1-v2)/(2*gravity*Dp_H*Rsd)**0.5)**2.73
    second = ((rho_s*(pi/6)*d**3)/rho_l)**0.094
    return 0.83*lambda1(Dp_H, v1, epsilon, nu_l) + 0.37*first*second


def fb_pressure_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, Cvb=0.6):
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
    Ap, A1, A2 = areas(Dp, Cvs, Cvb)
    Op, O1, O12, O2 = perimeters(Dp, Cvs, Cvb)
    Dp_H = 4*A1/(O1 + O12)
    v1 = vls*Ap/A1
    v2 = 0.0
    lbd1 = lambda1(Dp_H, v1, epsilon, nu)
    tau1_l = lbd1*rhol*v1**2/8
    F1_l = tau1_l * O1
    lbd12 = min(lambda12(Dp_H, d, v1, v2, nu),
                lambda12_sf(Dp_H, d, v1, v2, epsilon, nu, rhol, rhos))
    tau12_l = lbd12*rhol*v1**2/8
    F12_l = tau12_l * O12
    return (F1_l + F12_l)/A1


def fb_head_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, Cvb=0.6):
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
    delta_p = fb_pressure_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, Cvb)
    return delta_p * rhol/gravity


def sliding_bed_pressure_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, Cvb=0.6):
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
    im = sliding_bed_head_loss(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, Cvb)
    return im*gravity/rhol


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
    Erhg = 0.415
    il = fluid_head_loss(vls, Dp, epsilon, nu, rhol)
    Rsd = (rhos-rhol)/rhol
    return Erhg*Rsd*Cvs+il

if __name__ == '__main__':
    pass
