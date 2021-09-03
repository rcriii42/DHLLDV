"""
SystemTab: Create the tab with the system (pipeline and pumps) information

Execute by running 'bokeh serve --show .\Scripts\bokeh_viewer.py' to open a tab in your browser

Added by R. Ramsdell 01 September, 2021
"""
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Button, RadioButtonGroup
from bokeh.models import Spacer, Div, Panel, Tabs
from bokeh.plotting import figure

from DHLLDV.PipeObj import Pipeline

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
HQ_plot = figure(height=450, width=725, title="System Head Requirement",
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
HQ_plot.xaxis[0].axis_label = f'Velocity (m/sec in {pipeline.slurry.Dp:0.3f}m pipe)'
HQ_plot.yaxis[0].axis_label = 'Head (m/m)'
HQ_plot.axis.major_tick_in = 10
HQ_plot.axis.minor_tick_in = 7
HQ_plot.axis.minor_tick_out = 0
HQ_plot.legend.location = "top_left"

def update_all(pipeline):
    """Placeholder for an update function"""
    vls_list = pipeline.slurry.vls_list
    im_source.data=dict(v=vls_list,
                        im=[pipeline.calc_system_head(v)[0] for v in vls_list],
                        il=[pipeline.calc_system_head(v)[1] for v in vls_list],
                        )
    HQ_plot.xaxis[0].axis_label = f'Velocity (m/sec in {pipeline.slurry.Dp:0.3f}m pipe)'

def pipe_panel(i, pipe):
    """Create a Bokeh row with information about the pipe"""
    return row(TextInput(title="#", value=f'{i:3d}', width=45),
               TextInput(title="Name", value=pipe.name, width=95),
               TextInput(title="Dp (mm)", value=f"{int(pipe.diameter*1000)}", width=76),
               TextInput(title="Length (m)", value=f"{pipe.length:0.1f}", width=76),
               TextInput(title="Fitting K (-)", value=f"{pipe.total_K:0.2f}", width=76),
               TextInput(title="Delta z (m)", value=f"{pipe.elev_change:0.1f}", width=76),)

def system_panel(PL):
    """Create a Bokeh Panel with the system elements"""
    pipecol = column([pipe_panel(i, p) for i, p in enumerate(PL.pipesections)])
    return Panel(title="Pipeline", child = row(pipecol, HQ_plot))





