"""
SystemTab: Create the tab with the system (pipeline and pumps) information

Execute by running 'bokeh serve --show .\Scripts\bokeh_viewer.py' to open a tab in your browser

Added by R. Ramsdell 01 September, 2021
"""
import collections
from copy import copy

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Button, RadioButtonGroup
from bokeh.models import Spacer, Div, Panel, Tabs
from bokeh.plotting import figure

from DHLLDV import DHLLDV_framework
from DHLLDV.SlurryObj import Slurry

pipe = collections.namedtuple('pipe',
                              ('name', 'diameter', 'length', 'total_K', 'elev_change'),
                              )

class Pipeline():
    """Object to manage the pipeline system"""
    def __init__(self, pipe_list=None, slurry=None):
        if not slurry:
            self.slurry = Slurry()
        else:
            self.slurry = slurry
        if pipe_list:
            self.pipesections = pipe_list
        else:
            self.pipesections = [pipe('Entrance', self.slurry.Dp, 0, 0.5, -10.0),
                                 pipe('Discharge', self.slurry.Dp, 1000, 1.0, 1.5)]
        self.slurries = {self.slurry.Dp: self.slurry}
        for p in self.pipesections:
            if p.diameter not in self.slurries:
                self.slurries[p.diameter] = copy(self.slurry)
                self.slurries[p.diameter].Dp = p.diameter

pipeline = Pipeline()

def calc_system_head(PL, v, Cv=None):
    """Calculate the system head for a pipeline"""
    fitting_loss = 0
    elev_head = 0

    for p in pipe:
        if Cv and type(p.object) == Slurry:
            p.object.Cv = Cv

def update_all():
    """Placeholder for an update function"""
    pass

def pipe_panel(pipe):
    """Create a Bokeh row with information about the pipe"""
    return row(TextInput(title="Name", value=pipe.name, width=96),
               TextInput(title="Dp (mm)", value=f"{int(pipe.diameter*1000)}", width=76),
               TextInput(title="Length (m)", value=f"{pipe.length:0.1f}", width=76),
               TextInput(title="Fitting K (-)", value=f"{pipe.total_K:0.2f}", width=76),
               TextInput(title="Delta z (m)", value=f"{pipe.elev_change:0.1f}", width=76),)

def system_panel(PL):
    """Create a Bokeh Panel with the system elements"""
    return Panel(title="Pipeline", child = column([pipe_panel(p) for p in PL.pipesections]))





