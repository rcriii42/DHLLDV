"""Show the simulation in the browser"""

import base64
import copy
import io
from math import pi, sin, cos, tan, asin
import sys

import openpyxl

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Slider, Button, RadioButtonGroup, Label
from bokeh.models import Spacer, Div, TabPanel, Tabs, Dropdown, HoverTool, Range1d, LinearAxis, NumeralTickFormatter
from bokeh.models.tickers import FixedTicker
from bokeh.models.widgets import FileInput
from bokeh.plotting import figure

from DHLLDV import DHLLDV_framework
from DHLLDV.LagrPipe import LagrPipe, LagrPipeline
from DHLLDV.LagrFeeds import CyclicFeed, CSDFeed
from DHLLDV.PipeObj import Pipeline, Pipe, OperatingPointError
from DHLLDV.PumpObj import Pump
from DHLLDV.SlurryObj import Slurry

from CrossoverGauge import CrossoverGauge
from load_pump_excel import load_pipeline_from_workbook, InvalidExcelError
from unit_conv import unit_conv_US, unit_label_US, unit_conv_SI, unit_label_SI, convert_list

from ExamplePumps import Ladder_Pump600, Main_Pump500

unit_convs = unit_conv_SI
unit_labels = unit_label_SI

slurry = Slurry(fluid='salt', Cv=0.001)
pipe_list = [Pipe(name='Entrance', diameter=0.6, length=0, total_K=0.5, elev_change=-4.0),
             Pipe(name='LP Suction', diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0),
             Ladder_Pump600,
             Pipe(name='MP Suction', diameter=0.5, length=25.0, total_K=0.1, elev_change=0.0),
             Main_Pump500,
             Pipe(name='MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
             Pipe(name='Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)]
pipeline = Pipeline('test_pipeline', pipe_list, copy.deepcopy(slurry))
lpipeline = LagrPipeline(name="test lagrangian pipeline",
                         pipe_list=pipe_list,
                         slurry=slurry,
                         suct_feed=CSDFeed(copy.deepcopy(slurry), density=1.4, Dp=0.6, swing_time=60, corner_time=20,
                                           backswing_ratio=0.75))

vd_source = ColumnDataSource(data=dict(timestep=[], velocity=[], density_in=[], density_avg=[]))


def build_snake_source():
    """Build the source data for the pipeline snake"""
    snake_x = [0.0]
    snake_rho = [1.03]
    for p in lpipeline.lpipe_list:
        if type(p) is LagrPipe:
            for s in p.slugs:
                snake_x.append(snake_x[-1] + s.length)
                snake_rho.append(s.rhom)
    return snake_x, snake_rho


sx, sr = build_snake_source()
snake_source = ColumnDataSource(data=dict(x=sx, rho=sr))
snake_plot = figure(height=150, tools="xpan,xwheel_zoom,xbox_zoom,reset", y_axis_location="right",
                    y_range=(1.0, 1.6), x_range=(0.0, lpipeline.total_length))
snake_plot.step(x='x', y='rho', mode='before', source=snake_source)

crossover_gauge = CrossoverGauge(vel_max_value=9.0, den_max_value=1.5, pipe_dia=pipe_list[-1].diameter)

# velocity_plot = figure(height=150, tools="xpan,xwheel_zoom,xbox_zoom,reset", y_axis_location="right",
#                        y_range=(0.0, 10.0))
# velocity_plot.x_range.follow = "end"
# velocity_plot.x_range.follow_interval = 100
# velocity_plot.x_range.range_padding = 0
# velocity_plot.line(x='timestep', y='velocity', alpha=0.2, line_width=3, color='navy', source=vd_source)
#
# density_plot = figure(height=150, tools="xpan,xwheel_zoom,xbox_zoom,reset", y_axis_location="right",
#                       y_range=(1.0, 1.6))
# density_plot.x_range.follow = "end"
# density_plot.x_range.follow_interval = 100
# density_plot.x_range.range_padding = 0
# density_plot.line(x='timestep', y='density_in', alpha=0.8, line_width=2, color='orange', source=vd_source)
# density_plot.line(x='timestep', y='density_avg', alpha=0.8, line_width=2, color='red', source=vd_source)

time_step_display = TextInput(title="Timestep", value=f"{0}", width=95, disabled=True)
Vm_display = TextInput(title="Vm (m/s)", value=f"{0.0}", width=95, disabled=True)
Sm_in_display = TextInput(title="Rhom in (t/m3)", value=f"{0.0}", width=100, disabled=True)
Sm_avg_display = TextInput(title="Rhom avg (t/m3)", value=f"{0.0}", width=100, disabled=True)
prod_display = TextInput(title="Prod m3/Hr", value=f"{000}", width=100, disabled=True)

num_slugs_display = TextInput(title="Total slugs", value=f'{lpipeline.num_slugs}', disabled=True)

pipeline_info = Div(text=f'{lpipeline}'.replace('\n', '<BR>'),
                    styles={'font-size': '80%', 'color': 'blue'})
slurry_info = Div(text=f'{slurry}'.replace('\n', '<BR>'),
                  styles={'font-size': '80%', 'color': 'blue'})


def create_HQ_plot():
    """Create the HQ Plot"""
    flow_list = [pipeline.pipesections[-1].flow(v) for v in pipeline.slurry.vls_list]
    head_lists = list(zip(*[pipeline.calc_system_head(Q) for Q in flow_list]))
    source = ColumnDataSource(data=dict(Q=convert_list(unit_convs['flow'], flow_list),
                                        v=convert_list(unit_convs['len'], pipeline.slurry.vls_list),
                                        im=convert_list(unit_convs['len'], head_lists[0]),
                                        il=convert_list(unit_convs['len'], head_lists[1]),
                                        Hpump_l=convert_list(unit_convs['len'], head_lists[2]),
                                        Hpump_m=convert_list(unit_convs['len'], head_lists[3])))
    last10_src = ColumnDataSource(data=dict(Q=[], im=[]))
    last30_src = ColumnDataSource(data=dict(Q=[], im=[]))
    HQ_hover = HoverTool(tooltips=[('name', "$name"),
                                   (f"Flow ({unit_labels['flow']})", "@Q{0.00}"),
                                   (f"Velocity ({unit_labels['vel']})", "@v{0.0}"),
                                   (f"Slurry Graded Cvt=c ({unit_labels['len']})", "@im{0,0.0}"),
                                   (f"Fluid ({unit_labels['len']})", "@il{0,0.0}"),
                                   (f"Pump Head Slurry ({unit_labels['len']})", "@Hpump_m{0,0.0}",),
                                   (f"Pump Head Water ({unit_labels['len']})", "@Hpump_l{0,0.0}",),
                                   ])
    plot = figure(height=450, width=595, title="System Head Requirement",
                  tools="crosshair,pan,reset,save,wheel_zoom",
                  x_range=[0, flow_list[-1] * unit_convs['flow']], y_range=[0, 100])
    plot.tools.append(HQ_hover)

    plot.line('Q', 'im', source=source,
              color='black',
              line_dash='solid',
              line_width=3,
              line_alpha=0.6,
              legend_label=f'Slurry Graded Cvt=c ({unit_labels["len"]})',
              name='Slurry graded Sand Cvt=c')

    plot.line('Q', 'il', source=source,
              color='blue',
              line_dash='solid',
              line_width=2,
              line_alpha=0.3,
              legend_label='Water',
              name='Water')

    plot.line('Q', 'Hpump_m', source=source,
              color='black',
              line_dash='dashed',
              line_width=3,
              line_alpha=0.6,
              legend_label='Pump Slurry',
              name='Pump Slurry')

    plot.line('Q', 'Hpump_l', source=source,
              color='blue',
              line_dash='dashed',
              line_width=2,
              line_alpha=0.3,
              legend_label='Pump Water',
              name='Pump Water')

    plot.circle(x='Q', y='im', color='orange', size=4, alpha=1.0, source=last10_src)
    plot.circle(x='Q', y='im', color='orange', size=2, alpha=0.25, source=last30_src)
    plot.extra_x_ranges = {'vel_range': Range1d(pipeline.slurry.vls_list[0] * unit_convs['len'],
                                                pipeline.slurry.vls_list[-1] * unit_convs['len'])}
    plot.add_layout(LinearAxis(x_range_name='vel_range'), 'above')
    plot.xaxis[1].axis_label = f'Flow ({unit_labels["flow"]})'
    plot.xaxis[0].axis_label = f'Velocity ({unit_labels["vel"]} in {pipeline.slurry.Dp * unit_convs["dia"]:0.1f} ' \
                               f'{unit_labels["dia"]} pipe)'
    plot.xaxis[0].formatter = NumeralTickFormatter(format="0.0")
    plot.yaxis[0].axis_label = f'Head ({unit_labels["len"]})'
    plot.y_range.end = 2 * pipeline.calc_system_head(0.1)[3] * unit_convs['len']
    plot.axis.major_tick_in = 10
    plot.axis.minor_tick_in = 7
    plot.axis.minor_tick_out = 0
    plot.legend.location = "bottom_left"

    return plot, source, last10_src, last30_src


HQ_plot, im_source, last10_source, last30_source = create_HQ_plot()
HQ_panel = TabPanel(child=HQ_plot, title="HQ")


def update_HQ_plot():
    """Update the HQ plot from the given pipeline"""
    pipeline.slurry.rhom = lpipeline.suction_feed.rhom
    pipeline.update_slurries()
    this_pipe = Pipe(diameter=pipeline.slurry.Dp)
    flow_list = [this_pipe.flow(v) for v in pipeline.slurry.vls_list]
    head_lists = list(zip(*[pipeline.calc_system_head(Q) for Q in flow_list]))
    im_source.data = dict(Q=convert_list(unit_convs['flow'], flow_list),
                          v=convert_list(unit_convs['len'], pipeline.slurry.vls_list),
                          im=convert_list(unit_convs['len'], head_lists[0]),
                          il=convert_list(unit_convs['len'], head_lists[1]),
                          Hpump_l=convert_list(unit_convs['len'], head_lists[2]),
                          Hpump_m=convert_list(unit_convs['len'], head_lists[3]))
    last_hq = dict(Q=[lpipeline.lastflow], im=[lpipeline.last_head_loss * -1])
    last10_source.stream(last_hq, 1)
    last30_source.stream(last_hq, 30)

    HQ_plot.xaxis[0].axis_label = (f'Velocity ({unit_labels["vel"]} in '
                                   f'{pipeline.slurry.Dp * unit_convs["dia"]:0.1f} {unit_labels["dia"]} pipe)')
    HQ_plot.y_range.end = 2 * pipeline.calc_system_head(0.1)[3] * unit_convs['len']
    HQ_plot.x_range.end = flow_list[-1] * unit_convs['flow']


update_HQ_plot()


def update():
    """Update the simulation"""
    q, heads, disch_slug = lpipeline.update()
    in_slurry = lpipeline.lpipe_list[0].slugs[0].slurry
    new_data = dict(timestep=[lpipeline.timecounter],
                    velocity=[lpipeline.lpipe_list[-1].velocity(q)],
                    density_in=[in_slurry.rhom],
                    density_avg=[lpipeline.average_rhom],)

    time_step_display.value = f'{lpipeline.timecounter}'
    Vm_display.value = f'{lpipeline.lpipe_list[-1].velocity(q):0.3f}'
    Sm_in_display.value = f'{in_slurry.rhom:0.3f}'
    Sm_avg_display.value = f'{lpipeline.average_rhom:0.3f}'
    production = q * in_slurry.Cvi * 3600
    prod_display.value = f'{production:0.0f}'
    num_slugs_display.value = f'{lpipeline.num_slugs}'

    sx, sr = build_snake_source()
    snake_source.data = dict(x=sx, rho=sr)

    update_HQ_plot()
    crossover_gauge.update(lpipeline.lpipe_list[-1].velocity(q),
                           lpipeline.lpipe_list[0].slugs[0].rhom)

    print(f'Timestep {new_data["timestep"][-1]}: Velocity: {new_data["velocity"][-1]:0.2f}, '
          f'Incoming Density: {new_data["density_in"][-1]:0.3f}, Pipeline Density: {new_data["density_avg"][-1]:0.3f}, '
          f'Status: {lpipeline.suction_feed.status}')
    vd_source.stream(new_data, 100)


def load_xl_data(attr, old, new):
    """Load the pipeline from an Excel file"""
    global lpipeline, pipeline
    global slurry
    excel = io.BytesIO(base64.b64decode(file_input.value))
    try:
        pipeline = load_pipeline_from_workbook(openpyxl.load_workbook(filename=excel, data_only=True))
        slurry = pipeline.slurry
        lpipeline = LagrPipeline(pipe_list=pipeline.pipesections, slurry=slurry,
                                 suct_feed=CSDFeed(slurry, density=1.17),
                                 start_pipeline_density=1.03)
        source = ColumnDataSource(data=dict(timestep=[], velocity=[], density_in=[], density_avg=[]))
        pipeline_info.text = f'{lpipeline}'.replace('\n', '<BR>')
        slurry_info.text = f'{slurry}'.replace('\n', '<BR>')
    except InvalidExcelError as e:
        print(f'Error loading {file_input.filename}: {e}')

    crossover_gauge.update(lpipeline.lpipe_list[-1].velocity(1.0),  # Use 1 m3/sec for initial update
                           lpipeline.lpipe_list[0].slugs[0].rhom,
                           rhof=slurry.rhol, rhos=slurry.rhos, rhoi=slurry.rhoi, pipe_dia=slurry.Dp)
    update_HQ_plot()


file_input = FileInput(accept=".xls, .xlsm, .xlsx")
file_input.on_change('filename', load_xl_data)


periodic_callbacks = []
rate = 1


def update_framerate(attr, old, new):
    """Change the framerate of the simulation"""
    if len(periodic_callbacks) > 0:
        curdoc().remove_periodic_callback(periodic_callbacks.pop(0))
        periodic_callbacks.append(curdoc().add_periodic_callback(update, (21 - new)*50))


rate_slider = Slider(title="framerate", value=rate, start=1, end=20, step=1)
rate_slider.on_change('value', update_framerate)


def start_button_clicked():
    """Start or stop the simulation"""
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
    """Stop the server"""
    sys.exit()


stop_button = Button(label="Stop Server", button_type="success", width=75)
stop_button.on_click(stop_button_callback)

left_column = column(row(time_step_display, Vm_display, Sm_in_display, Sm_avg_display, prod_display),
                     column(crossover_gauge.figure, snake_plot))
right_column = Tabs(tabs=[HQ_panel])
bottom_column = column(row(start_button, rate_slider),
                       stop_button,
                       num_slugs_display,
                       file_input,
                       row(slurry_info, pipeline_info))
curdoc().add_root(column(row(left_column, right_column), bottom_column))
curdoc().title = "Simulation"
