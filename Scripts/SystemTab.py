"""
SystemTab: Create the tab with the system (pipeline and pumps) information

Execute by running 'bokeh serve --show .\Scripts\bokeh_viewer.py' to open a tab in your browser

Added by R. Ramsdell 01 September, 2021
"""
import collections

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Button, RadioButtonGroup
from bokeh.models import Spacer, Div, Panel, Tabs
from bokeh.plotting import figure

from DHLLDV import DHLLDV_framework
from DHLLDV.SlurryObj import Slurry

pipe = collections.namedtuple('pipe',
                              ('name', 'object', 'diameter', 'length', 'total_K', 'elev_change'),
                              )

pipeline = (pipe('Entrance', None, 0, 0, 0.5, -10.0),
            pipe('Suction', Slurry(Dp=0.863), 0.863, 38.0, 0.35, 10),
            pipe('Discharge', Slurry(), 0.762, 1000, 1.0, 1.5))

def update_all():
    """Placeholder for an update function"""
    pass

def pipe_panel(pipe):
    """Create a Bokeh row with information about the pipe"""
    return row(TextInput(title="Name", value=pipe.name, width=76),
               TextInput(title="Dp (mm)", value=f"{int(pipe.diameter*1000)}", width=76),
               TextInput(title="Length (m)", value=f"{pipe.length:0.1f}", width=76),
               TextInput(title="Fitting K (-)", value=f"{pipe.total_K:0.2f}", width=76),
               TextInput(title="Delta z (m)", value=f"{pipe.elev_change:0.1f}", width=76),)

def system_panel(PL):
    """Create a Bokeh Panel with the system elements"""
    return Panel(title="Pipline", child = column([pipe_panel(p) for p in PL]))





