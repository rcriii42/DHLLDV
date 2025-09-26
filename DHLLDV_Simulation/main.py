"""Show the simulation in the browser"""

import base64
import io
import sys

import openpyxl

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Slider, Button, RadioButtonGroup
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

from load_pump_excel import load_pipeline_from_workbook, InvalidExcelError

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

velocity_plot = figure(height=200, tools="xpan,xwheel_zoom,xbox_zoom,reset", y_axis_location="right",
                       y_range=(0.0, 10.0))
velocity_plot.x_range.follow = "end"
velocity_plot.x_range.follow_interval = 100
velocity_plot.x_range.range_padding = 0
velocity_plot.line(x='timestep', y='velocity', alpha=0.2, line_width=3, color='navy', source=source)

density_plot = figure(height=200, tools="xpan,xwheel_zoom,xbox_zoom,reset", y_axis_location="right",
                      y_range=(1.0, 1.6))
density_plot.x_range.follow = "end"
density_plot.x_range.follow_interval = 100
density_plot.x_range.range_padding = 0
density_plot.line(x='timestep', y='density_in', alpha=0.8, line_width=2, color='orange', source=source)
density_plot.line(x='timestep', y='density_avg', alpha=0.8, line_width=2, color='red', source=source)

Vm_display = TextInput(title="Vm (m/s)", value=f"{0.0}", width=95, disabled=True)
Sm_in_display = TextInput(title="Rhom in (ton/m3)", value=f"{0.0}", width=100, disabled=True)
Sm_avg_display = TextInput(title="Rhom avg (ton/m3)", value=f"{0.0}", width=100, disabled=True)
pipeline_info = Div(text=f'{lpipeline}'.replace('\n', '<BR>'),
                    styles={'font-size': '80%', 'color': 'blue'})
slurry_info = Div(text=f'{slurry}'.replace('\n', '<BR>'),
                  styles={'font-size': '80%', 'color': 'blue'})


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

    print(new_data)
    source.stream(new_data, 100)


def load_xl_data(attr, old, new):
    global lpipeline
    global slurry
    excel = io.BytesIO(base64.b64decode(file_input.value))
    try:
        pipeline = load_pipeline_from_workbook(openpyxl.load_workbook(filename=excel, data_only=True))
        slurry = pipeline.slurry
        lpipeline = LagrPipeline(pipe_list=pipeline.pipesections, slurry=slurry,
                                 suct_feed=CyclicFeed(slurry, densities=csd_densities, Dp=0.6))
        source = ColumnDataSource(data=dict(timestep=[], velocity=[], density_in=[], density_avg=[]))
        pipeline_info.text = f'{lpipeline}'.replace('\n', '<BR>')
        slurry_info.text = f'{slurry}'.replace('\n', '<BR>')
    except InvalidExcelError as e:
        print(f'Error loading {file_input.filename}: {e}')


file_input = FileInput(accept=".xls, .xlsm, .xlsx")
file_input.on_change('filename', load_xl_data)


periodic_callbacks = []
rate = 1
def update_framerate(attr, old, new):
    rate = new
    print(f'{rate=}')
    if len(periodic_callbacks) > 0:
        curdoc().remove_periodic_callback(periodic_callbacks.pop(0))
        periodic_callbacks.append(curdoc().add_periodic_callback(update, (21 - new)*50))
rate_slider = Slider(title="framerate", value=rate, start=1, end=20, step=1)
rate_slider.on_change('value', update_framerate)
print(f'{rate=}')


def start_button_clicked():
    """Start or stop the simulation"""
    print('Button clicked')
    if len(periodic_callbacks) > 0:
        print("Stopping simulation")
        curdoc().remove_periodic_callback(periodic_callbacks.pop(0))
        start_button.label = "Start"
    else:
        print("Starting simulation")
        periodic_callbacks.append(curdoc().add_periodic_callback(update, (21 - rate) * 50))
        start_button.label = "Stop"
start_button = Button(label="Start", button_type="success")
start_button.on_click(start_button_clicked)

# Button to stop the server
def stop_button_callback():
    sys.exit()  # Stop the server
stop_button = Button(label="Stop Server", button_type="success", width=75)
stop_button.on_click(stop_button_callback)

curdoc().add_root(column(file_input,
                         row(Vm_display, Sm_in_display, Sm_avg_display),
                         velocity_plot,
                         density_plot,
                         row(start_button, rate_slider), stop_button,
                         row(slurry_info, pipeline_info)
                         )
                  )
curdoc().title = "Simulation"
