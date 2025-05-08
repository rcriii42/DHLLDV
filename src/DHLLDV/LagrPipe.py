"""LagrPipe.py - Pipe and Pipeline objects for the pumping simulation

Creates a Lagrangian view of the pipeline that tracks 'slugs' of slurry moving down the pipeline
"""

from collections.abc import Callable, Awaitable
from copy import copy
from dataclasses import dataclass
from math import pi
from types import FunctionType

import scipy.optimize
from DHLLDV.DHLLDV_constants import gravity
from DHLLDV.PumpObj import Pump
from DHLLDV.SlurryObj import Slurry
from DHLLDV.PipeObj import Pipe, Pipeline


def add_slurries(sw1: [Slurry | None, float], sw2: [Slurry | None, float]) -> Slurry:
    """Create a weighted average of two slurries

    Returns a new Slurry with averaged density, eventually needs to combine the GSDs, etc"""
    if sw1[0] is None:
        return sw2[0]
    elif sw2[0] is None:
        return sw1[0]
    rho_new = (sw1[0].rhom * sw1[1] + sw2[0].rhom * sw2[1])/(sw1[1] + sw2[1])
    new_slurry = copy(sw2[0])
    new_slurry.rhom = rho_new
    return new_slurry
