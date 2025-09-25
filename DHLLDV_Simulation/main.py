"""Show the simulation in the browser"""

import base64
import io
import sys

import openpyxl

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Button, RadioButtonGroup
from bokeh.models import Spacer, Div, TabPanel, Tabs, Dropdown
from bokeh.models.tickers import FixedTicker
from bokeh.models.widgets import FileInput
from bokeh.plotting import figure

from DHLLDV import DHLLDV_framework, LagrPipe
from DHLLDV.LagrPipe import LagrPipeline
from DHLLDV.LagrFeeds import CyclicFeed
from DHLLDV.PipeObj import Pipeline, Pipe, OperatingPointError
from DHLLDV.PumpObj import Pump
from DHLLDV.SlurryObj import Slurry

from ExamplePumps import Ladder_Pump600, Main_Pump500

csd_densities = ([1.03] * 15 +  # coming out of corner
                 [1.35] * 60 * 2 +  # dig swing
                 [1.19] * 15 + [1.03] * 15 +  # corner
                 [1.35/2] * 60 * 2 +  # back swing
                 [1.35/4]*15)

slurry = Slurry(fluid='salt', Cv=0.001)
pipe_list = [Pipe(name='Entrance', diameter=0.6, length=0, total_K=0.5, elev_change=-4.0),
             Pipe(name='LP Suction', diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0),
             Ladder_Pump600,
             Pipe(name='MP Suction', diameter=0.5, length=25.0, total_K=0.1, elev_change=0.0),
             Main_Pump500,
             Pipe(name='MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
             Pipe(name='Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)]
lpipeline = LagrPipeline(name="test lagrangian pipeline",
                         pipe_list=pipe_list,
                         slurry=slurry,
                         suct_feed=CyclicFeed(slurry, densities=csd_densities, Dp=0.6))

source = ColumnDataSource(data=dict(timestep=[], velocity=[], density_in=[], density_avg=[]))

p = figure(height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset",
           y_axis_location="right")
p.x_range.follow = "end"
p.x_range.follow_interval = 100
p.x_range.range_padding = 0

p.line(x='timestep', y='velocity', alpha=0.2, line_width=3, color='navy', source=source)
p.line(x='timestep', y='density_in', alpha=0.8, line_width=2, color='orange', source=source)
p.line(x='timestep', y='density_avg', alpha=0.8, line_width=2, color='red', source=source)

Vm_display = TextInput(title="Vm (m/s)", value=f"{0.0}", width=95, disabled=True)
Sm_in_display = TextInput(title="Rhom in (ton/m3)", value=f"{0.0}", width=100, disabled=True)
Sm_avg_display = TextInput(title="Rhom avg (ton/m3)", value=f"{0.0}", width=100, disabled=True)


def update():
    """Update the simulation"""
    q, heads, disch_slug = lpipeline.update()
    new_data = dict(timestep=[lpipeline.timecounter],
                    velocity=[lpipeline.lpipe_list[-1].velocity(q)],
                    density_in=[lpipeline.lpipe_list[0].slugs[0].rhom],
                    density_avg=[lpipeline.average_rhom()],)

    Vm_display.value = f'{lpipeline.lpipe_list[-1].velocity(q):0.3f}'
    Sm_in_display.value = f'{lpipeline.lpipe_list[0].slugs[0].rhom:0.3f}'
    Sm_avg_display.value = f'{lpipeline.average_rhom():0.3f}'

    source.stream(new_data, 100)


curdoc().add_root(column(row(Vm_display, Sm_in_display, Sm_avg_display), p))
curdoc().add_periodic_callback(update, 1000)
curdoc().title = "Simulation"
