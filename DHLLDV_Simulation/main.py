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


class CrossoverGauge:
    """A class to simulate a crossover velocity/density gauge with a middle axis indicating production"""
    def __init__(self,
                 vel_max_angle=45, vel_max_value=5.5, vel_pointer_origin=(1, 0),
                 den_max_angle=45, den_max_value=1.3, den_pointer_origin=(-1, 0),
                 rhof=1.025, rhos=2.65, rhoi=1.95, pipe_dia=(10/12)*0.3048) -> None:
        self.vel_max_angle = vel_max_angle
        self.vel_min_value = 0.0
        self.vel_max_value = vel_max_value
        self.vel_pointer_origin = vel_pointer_origin
        self.den_max_angle = den_max_angle
        self.den_min_value = 1.0
        self.den_max_value = den_max_value
        self.den_pointer_origin = den_pointer_origin

        self.rhof = rhof
        self.rhos = rhos
        self.rhoi = rhoi
        self.Dp = pipe_dia

        self.tick_len = 1.05  # Length of the tick relative to the axis radius

        self.figure = figure(height=375,
                             x_range=(den_pointer_origin[0]*1.5, vel_pointer_origin[0]*1.5),
                             y_range=(-0.1, 0.85 * (self.vel_pointer_origin[0] - self.den_pointer_origin[0])),
                             tools="", outline_line_color="black")
        self.figure.xaxis.visible = False
        self.figure.yaxis.visible = False
        self.draw_side_axis('vel')
        self.draw_side_axis('den')
        self.draw_middle_axis()

        self.pointer_data = ColumnDataSource(data=dict(vel_x=[vel_pointer_origin[0], den_pointer_origin[0]],
                                                       vel_y=[vel_pointer_origin[1], den_pointer_origin[1]],
                                                       den_x=[den_pointer_origin[0], vel_pointer_origin[0]],
                                                       den_y=[den_pointer_origin[1], vel_pointer_origin[1]]))
        self.figure.line(source=self.pointer_data, x='vel_x', y='vel_y', color="red")
        self.figure.line(source=self.pointer_data, x='den_x', y='den_y', color="red")
        self.update(vel_max_value/2, 1+(den_max_value-1)/2)

    @property
    def Ap(self):
        """Return the area of the pipe in m2"""
        return pi * (self.Dp / 2)**2

    def update(self, vel, den):
        """Update the crossover gauge pointers"""
        pointer_radius = (self.vel_pointer_origin[0] - self.den_pointer_origin[0]) * 1 + (self.tick_len - 1) / 2
        vel_angle = pi - (vel * self.vel_max_angle / self.vel_max_value) * pi / 180
        den_angle = ((den - 1) * self.den_max_angle / (self.den_max_value - 1)) * pi / 180
        self.pointer_data.data = dict(vel_x=[self.vel_pointer_origin[0],
                                             self.vel_pointer_origin[0] + pointer_radius * cos(vel_angle)],
                                      vel_y=[self.vel_pointer_origin[1],
                                             self.vel_pointer_origin[1] + pointer_radius * sin(vel_angle)],
                                      den_x=[self.den_pointer_origin[0],
                                             self.den_pointer_origin[0] + pointer_radius * cos(den_angle)],
                                      den_y=[self.den_pointer_origin[1],
                                             self.den_pointer_origin[1] + pointer_radius * sin(den_angle)])

    def draw_middle_axis(self):
        """Calculate and draw the middle axis"""
        for i in range(1, 6):
            x_center = 0
            y_center = i * 0.2
            angle_center = asin((y_center - self.vel_pointer_origin[1]) /
                                ((x_center - self.vel_pointer_origin[0])**2 +
                                 (y_center - self.vel_pointer_origin[1])**2)**0.5)
            vel_center = angle_center * self.vel_max_value / (self.vel_max_angle * pi / 180)
            den_center = angle_center * (self.den_max_value - 1) / (self.den_max_angle * pi / 180) + 1
            prod_center = vel_center * self.Ap * ((den_center - self.rhof)/(self.rhoi - self.rhof))
            self.figure.add_layout(Label(x=x_center - 0.08, y=y_center + 0.02, text=f'{prod_center*3600:0.0f}'))

            # Now draw points of equal production starting at the maximum density
            x_list = [x_center]
            y_list = [y_center]
            den_min_angle = ((self.rhof - 1) * self.den_max_angle / (self.den_max_value - 1)) * pi / 180
            alpha_d = self.den_max_angle * 1.01 * pi / 180
            delta_alpha = (alpha_d - den_min_angle) / 10
            i = 11
            while True:
                # Lower density and calculate the velocity that maintains production
                if i <= 0:
                    break
                rhom = 1 + (self.den_max_value - 1) * alpha_d / (self.den_max_angle * pi / 180)
                if rhom <= self.rhof:
                    # One more point at maximum velocity
                    vm = self.vel_max_value * 1.01
                    rhom = prod_center * (self.rhoi - self.rhof)/(vm * self.Ap) + self.rhof
                    alpha_d = (rhom - 1) * (self.den_max_angle * pi / 180) / (self.den_max_value - 1)

                    i = 0   # End the loop after this point
                i -= 1
                Cvi = (rhom - self.rhof) / (self.rhoi - self.rhof)
                vm = prod_center / (Cvi * self.Ap)
                if vm > self.vel_max_value:
                    # One more point at maximum velocity
                    vm = self.vel_max_value * 1.01
                    rhom = prod_center * (self.rhoi - self.rhof) / (vm * self.Ap) + self.rhof
                    alpha_d = (rhom - 1) * (self.den_max_angle * pi / 180) / (self.den_max_value - 1)
                    i = 0

                # The angles of the velocity and density pointers
                alpha_v = pi - vm * (self.vel_max_angle * pi / 180) / self.vel_max_value
                # alpha_d = (rhom - self.rhof) * self.den_max_angle * pi / 180 / (self.den_max_value - self.rhof)

                # The x,y position
                xc = (self.den_pointer_origin[0] * tan(alpha_d) - self.vel_pointer_origin[0] * tan(alpha_v) +
                      self.vel_pointer_origin[1] - self.den_pointer_origin[1]) / (tan(alpha_d) - tan(alpha_v))
                yc = ((xc - self.vel_pointer_origin[0]) * tan(alpha_v) + self.vel_pointer_origin[1])
                if rhom > den_center:
                    x_list.insert(-1, xc)
                    y_list.insert(-1, yc)
                elif rhom < den_center:
                    x_list.append(xc)
                    y_list.append(yc)
                else:
                    pass
                alpha_d -= delta_alpha

            self.figure.line(x=x_list, y=y_list, color="blue")

    def draw_side_axis(self, side='vel'):
        """Draw the velocity axis on the left"""
        side_axis_radius = self.vel_pointer_origin[0] - self.den_pointer_origin[0]
        if side == 'vel':
            side_origin_x = self.vel_pointer_origin[0]
            side_origin_y = self.vel_pointer_origin[1]
            side_start_angle = pi
            side_end_angle = pi - self.vel_max_angle * pi / 180
            side_min_tick = self.vel_min_value
            side_tick_gap = 0.5
            side_num_ticks = int((self.vel_max_value - self.vel_min_value) / side_tick_gap) + 1
            if side_num_ticks > 10:
                side_tick_gap = 1.0
                side_num_ticks = int((self.vel_max_value - self.vel_min_value) / side_tick_gap) + 1
            side_tick_anchor = 'center_right'

            def delta_tick(tick_val):
                """Determine the tick angle offset from horiz based on the value"""
                return (-1 * tick_val * self.vel_max_angle / self.vel_max_value) * pi / 180
        else:
            side_origin_x = self.den_pointer_origin[0]
            side_origin_y = self.den_pointer_origin[1]
            side_start_angle = 0
            side_end_angle = self.den_max_angle * pi / 180
            side_min_tick = self.den_min_value
            side_tick_gap = .05
            side_num_ticks = int((self.den_max_value - self.den_min_value) / side_tick_gap) + 1
            side_tick_anchor = 'center_left'

            def delta_tick(tick_val):
                """Determine the tick angle offset from horiz based on the value"""
                return (tick_val - 1) * self.den_max_angle / (self.den_max_value - 1) * pi / 180
        # The axis line is an arc centered on the pointer origin and touching the other.
        num_segments = 50
        segment_angle = (side_end_angle - side_start_angle)/num_segments
        axis_angles = [side_start_angle + a * segment_angle for a in range(num_segments + 1)]
        axis_x = [side_origin_x + side_axis_radius*cos(a) for a in axis_angles]
        axis_y = [side_origin_y + side_axis_radius*sin(a) for a in axis_angles]
        self.figure.line(x=axis_x, y=axis_y)

        # The axis tick marks
        for i in range(side_num_ticks):
            tick_value = side_min_tick + i * side_tick_gap
            tick_angle = side_start_angle + delta_tick(tick_value)
            x_ticks = [side_origin_x + side_axis_radius*cos(tick_angle),
                       side_origin_x + self.tick_len*side_axis_radius*cos(tick_angle)]
            y_ticks = [side_origin_y + side_axis_radius*sin(tick_angle),
                       side_origin_y + self.tick_len*side_axis_radius*sin(tick_angle)]
            self.figure.line(x=x_ticks,
                             y=y_ticks)
            if side_tick_anchor == "center_right":
                x_offset = -0.2
            else:
                x_offset = 0.0
            self.figure.add_layout(Label(x=x_ticks[1]+x_offset, y=y_ticks[1], text=f'{tick_value:0.2f}'))


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

velocity_plot = figure(height=150, tools="xpan,xwheel_zoom,xbox_zoom,reset", y_axis_location="right",
                       y_range=(0.0, 10.0))
velocity_plot.x_range.follow = "end"
velocity_plot.x_range.follow_interval = 100
velocity_plot.x_range.range_padding = 0
velocity_plot.line(x='timestep', y='velocity', alpha=0.2, line_width=3, color='navy', source=vd_source)

density_plot = figure(height=150, tools="xpan,xwheel_zoom,xbox_zoom,reset", y_axis_location="right",
                      y_range=(1.0, 1.6))
density_plot.x_range.follow = "end"
density_plot.x_range.follow_interval = 100
density_plot.x_range.range_padding = 0
density_plot.line(x='timestep', y='density_in', alpha=0.8, line_width=2, color='orange', source=vd_source)
density_plot.line(x='timestep', y='density_avg', alpha=0.8, line_width=2, color='red', source=vd_source)

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
          f'Incoming Density: {new_data["density_in"][-1]:0.3f}, Pipeline Density: {new_data["density_avg"][-1]:0.3f}')
    vd_source.stream(new_data, 100)


def load_xl_data(attr, old, new):
    global lpipeline
    """Load the pipeline from an Excel file"""
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
