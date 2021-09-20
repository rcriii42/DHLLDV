"""
SystemTab: Create the tab with the system (pipeline and pumps) information

Execute by running 'bokeh serve --show .\Scripts\bokeh_viewer.py' to open a tab in your browser

Added by R. Ramsdell 01 September, 2021
"""
import copy

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Button, RadioButtonGroup
from bokeh.models import Spacer, Div, Panel, Tabs, LinearAxis, Range1d
from bokeh.plotting import figure

from DHLLDV.PipeObj import Pipeline, Pipe
from DHLLDV.PumpObj import Pump
from ExamplePumps import Ladder_Pump, Main_Pump

pipeline = Pipeline() #        Name             Dia     L    K      dZ
pipeline.pipesections = [Pipe('Entrance',      0.864,  0.0, 0.50, -10.0),
                         Pipe('UWP Suction',   0.864, 15.0, 0.05,   5.0),
                         copy.copy(Ladder_Pump),
                         Pipe('MP1 Suction',   0.864, 20.0, 0.30,  10.0),
                         copy.copy(Main_Pump),
                         Pipe('MP2 Suction',   0.864,  5.0, 0.30,   0.0),
                         copy.copy(Main_Pump),
                         Pipe('MP2 Discharge', 0.762, 60.0, 0.45,  -5.0),
                         Pipe('Float Hose',    0.762,600.0, 0.20,   0.0),
                         Pipe('Riser',         0.762, 40.0, 0.60, -10.0),
                         Pipe('Submerged Pipe',0.762,3000.0,0.20,  11.5),
                         Pipe('Shore Pipe',    0.762,750.0, 9.80,   0.0)]
pipeline.update_slurries()

flow_list = [pipeline.pipesections[-1].flow(v) for v in pipeline.slurry.vls_list]
im_source = ColumnDataSource(data=dict(Q=flow_list,
                                       im=[pipeline.calc_system_head(Q)[0] for Q in flow_list],
                                       il=[pipeline.calc_system_head(Q)[1] for Q in flow_list],
                                       Hpump_l = [pipeline.calc_system_head(Q)[2] for Q in flow_list],
                                       Hpump_m = [pipeline.calc_system_head(Q)[3] for Q in flow_list]
                                       ))

HQ_TOOLTIPS = [('name', "$name"),
               ("Flow (m\u00b3/sec)", "@Q"),
               ("Slurry Graded Cvt=c (m/m)", "@im"),
               ("Fluid (m/m)", "@il"),
               ("Pump Head Slurry", "@Hpump_m",),
               ("Pump Head Water", "@Hpump_l",),
              ]
HQ_plot = figure(height=450, width=725, title="System Head Requirement",
                 tools="crosshair,pan,reset,save,wheel_zoom",
                 #x_range=[0, 10], y_range=[0, 0.6],
                 tooltips=HQ_TOOLTIPS)

HQ_plot.line('Q', 'im', source=im_source,
             color='black',
             line_dash='dashed',
             line_width=3,
             line_alpha=0.6,
             legend_label='Slurry Graded Cvt=c (m/m)',
             name='Slurry graded Sand Cvt=c')

HQ_plot.line('Q', 'il', source=im_source,
             color='blue',
             line_dash='dashed',
             line_width=2,
             line_alpha=0.3,
             legend_label='Water',
             name='Water')

HQ_plot.line('Q', 'Hpump_m', source=im_source,
             color='black',
             line_dash='dashed',
             line_width=3,
             line_alpha=0.6,
             legend_label='Pump Slurry',
             name='Pump Slurry')

HQ_plot.line('Q', 'Hpump_l', source=im_source,
             color='blue',
             line_dash='dashed',
             line_width=2,
             line_alpha=0.3,
             legend_label='Pump Water',
             name='Pump Water')
HQ_plot.extra_x_ranges = {'vel_range': Range1d(pipeline.slurry.vls_list[0], pipeline.slurry.vls_list[-1])}
HQ_plot.add_layout(LinearAxis(x_range_name='vel_range'), 'above')
HQ_plot.xaxis[1].axis_label = f'Flow (m\u00b3/sec)'
HQ_plot.xaxis[0].axis_label = f'Velocity (m/sec in {pipeline.slurry.Dp:0.3f}m pipe)'
HQ_plot.yaxis[0].axis_label = 'Head (m/m)'
HQ_plot.axis.major_tick_in = 10
HQ_plot.axis.minor_tick_in = 7
HQ_plot.axis.minor_tick_out = 0


HQ_plot.legend.location = "top_left"

def update_all(pipeline):
    """Placeholder for an update function"""
    flow_list = [pipeline.pipesections[-1].flow(v) for v in pipeline.slurry.vls_list]
    im_source.data=dict(Q=flow_list,
                        im=[pipeline.calc_system_head(Q)[0] for Q in flow_list],
                        il=[pipeline.calc_system_head(Q)[1] for Q in flow_list],
                        Hpump_l = [pipeline.calc_system_head(Q)[2] for Q in flow_list],
                        Hpump_m = [pipeline.calc_system_head(Q)[3] for Q in flow_list])
    HQ_plot.xaxis[1].axis_label = f'Velocity (m/sec in {pipeline.slurry.Dp:0.3f}m pipe)'
    for i, r in enumerate(pipecol.children):    # iterate over the rows of pipe
        if isinstance(pipeline.pipesections[i], Pipe):
            r.children[2].value = f"{pipeline.pipesections[i].diameter:0.3f}"

def pipe_panel(i, pipe):
    """Create a Bokeh row with information about the pipe"""
    if isinstance(pipe, Pipe):
        return row(TextInput(title="#", value=f'{i:3d}', width=45),
                   TextInput(title="Name", value=pipe.name, width=95),
                   TextInput(title="Dp (m)", value=f"{pipe.diameter:0.3f}", width=76),
                   TextInput(title="Length (m)", value=f"{pipe.length:0.1f}", width=76),
                   TextInput(title="Fitting K (-)", value=f"{pipe.total_K:0.2f}", width=76),
                   TextInput(title="Delta z (m)", value=f"{pipe.elev_change:0.1f}", width=76),)
    elif isinstance(pipe, Pump):
        return row(TextInput(title="#", value=f'{i:3d}', width=45),
                   TextInput(title="Name", value=pipe.name, width=95),
                   TextInput(title="Suction (m)", value=f"{pipe.suction_dia:0.3f}", width=76),
                   TextInput(title="Discharge (m)", value=f"{pipe.disch_dia:0.3f}", width=76),
                   TextInput(title="Impeller (m)", value=f"{pipe.design_impeller:0.3f}", width=76),
                   TextInput(title="Speed (Hz)", value=f"{pipe.current_speed:0.3f}", width=76),)
    else:
        return row(TextInput(value="Unknown Item", width=76),)

pipecol = column([pipe_panel(i, p) for i, p in enumerate(pipeline.pipesections)])

def system_panel(PL):
    """Create a Bokeh Panel with the system elements"""
    return Panel(title="Pipeline", child = row(pipecol, HQ_plot))





