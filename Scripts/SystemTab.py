"""
SystemTab: Create the tab with the system (pipeline and pumps) information

Execute by running 'bokeh serve --show .\Scripts\bokeh_viewer.py' to open a tab in your browser

Added by R. Ramsdell 01 September, 2021
"""
import bisect
import collections
from copy import copy

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Button, RadioButtonGroup
from bokeh.models import Spacer, Div, Panel, Tabs
from bokeh.plotting import figure

from DHLLDV import DHLLDV_framework
from DHLLDV.SlurryObj import Slurry
from DHLLDV.DHLLDV_constants import gravity

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
                self.slurries[p.diameter].generate_curves()

    @property
    def Cv(self):
        return self.slurry.Cv

    @Cv.setter
    def Cv(self, Cv):
        """Allow the user to set the Cv for the entire system"""
        for s in self.slurries.values():
            s.Cv = Cv
            s.generate_curves()

    def calc_system_head(self, v):
        """Calculate the system head for a pipeline

        v is the velocity in m/sec

        returns a tuple, im, il"""
        rhom = self.slurry.rhom
        Hv = v**2/(2*gravity)
        delta_z = -1 * self.pipesections[0].elev_change
        Hfit = Hv       # Includes exit loss
        Hfric_m = 0
        Hfric_l = 0
        for p in self.pipesections:
            Hfit += p.total_K*Hv
            delta_z += p.elev_change
            index = bisect.bisect_left(self.slurries[p.diameter].vls_list, v)
            im = self.slurries[p.diameter].im_curves['graded_Cvt_im'][index]
            Hfric_m += im * p.length
            index = bisect.bisect_left(self.slurries[p.diameter].vls_list, v)
            il = self.slurries[p.diameter].im_curves['il'][index]
            Hfric_l += il * p.length
        return (Hfric_m + (Hfit +  + delta_z) * self.slurry.rhom,
                Hfric_l + (Hfit + + delta_z) * self.slurry.rhol)

pipeline = Pipeline()

vls_list = pipeline.slurry.vls_list
im_source = ColumnDataSource(data=dict(v=vls_list,
                                       im=[pipeline.calc_system_head(v)[0] for v in vls_list],
                                       il=[pipeline.calc_system_head(v)[1] for v in vls_list],
                                       ))

HQ_TOOLTIPS = [('name', "$name"),
               ("vls (m/sec)", "@v"),
               ("Slurry Graded Cvt=c (m/m)", "@im"),
               ("Fluid (m/m)", "@il"),
              ]
HQ_plot = figure(height=450, width=725, title="im curves",
                 tools="crosshair,pan,reset,save,wheel_zoom",
                 #x_range=[0, 10], y_range=[0, 0.6],
                 tooltips=HQ_TOOLTIPS)

HQ_plot.line('v', 'im', source=im_source,
             color='black',
             line_dash='dashed',
             line_width=3,
             line_alpha=0.6,
             legend_label='Slurry Graded Cvt=c (m/m)',
             name='Slurry graded Sand Cvt=c')

HQ_plot.line('v', 'il', source=im_source,
             color='blue',
             line_dash='dashed',
             line_width=2,
             line_alpha=0.3,
             legend_label='Water',
             name='Water')
HQ_plot.xaxis[0].axis_label = 'Velocity (m/sec)'
HQ_plot.yaxis[0].axis_label = 'Head (m/m)'
HQ_plot.axis.major_tick_in = 10
HQ_plot.axis.minor_tick_in = 7
HQ_plot.axis.minor_tick_out = 0
HQ_plot.legend.location = "top_left"

def update_all():
    """Placeholder for an update function"""



def pipe_panel(pipe):
    """Create a Bokeh row with information about the pipe"""
    return row(TextInput(title="Name", value=pipe.name, width=95),
               TextInput(title="Dp (mm)", value=f"{int(pipe.diameter*1000)}", width=76),
               TextInput(title="Length (m)", value=f"{pipe.length:0.1f}", width=76),
               TextInput(title="Fitting K (-)", value=f"{pipe.total_K:0.2f}", width=76),
               TextInput(title="Delta z (m)", value=f"{pipe.elev_change:0.1f}", width=76),)

def system_panel(PL):
    """Create a Bokeh Panel with the system elements"""
    pipecol = column([pipe_panel(p) for p in PL.pipesections])
    return Panel(title="Pipeline", child = row(pipecol, HQ_plot))





