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

@dataclass
class LagrPipe(Pipe):
    """A Lagrangian view of the pipe that tracks 'slugs' of slurry moving through the pipe section """
    slugs: list[(float, Slurry)] | None = None
    feed: Callable[[float], (float, Slurry)] | None = None  # Stub for the feed function

