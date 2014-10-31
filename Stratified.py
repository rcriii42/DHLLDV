'''
stratified.py - Calculations of fixed and sliding bed transport

Created on Oct 22, 2014

@author: RCRamsdell
'''

from DHLLDV_constants import gravity, Arel_to_beta
from math import pi, sin

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
    
if __name__ == '__main__':
    pass