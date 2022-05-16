"""
SystemTab: Create the tab with the system (pipeline and pumps) information

Execute by running 'bokeh serve --show .\Scripts\bokeh_viewer.py' to open a tab in your browser

Added by R. Ramsdell 01 September, 2021
"""
import copy

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput
from bokeh.models import Spacer, Panel, LinearAxis, Range1d, Div, NumeralTickFormatter
from bokeh.plotting import figure

from DHLLDV.PipeObj import Pipeline, Pipe
from DHLLDV.PumpObj import Pump
from ExamplePumps import Ladder_Pump, Main_Pump, base_slurry

setups = {"Example": Pipeline(pipe_list=[Pipe('Entrance', 0.6, 0, 0.5, -4.0),
                                         Pipe(diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0),
                                         copy.copy(Ladder_Pump),
                                         Pipe('MP Suction', 0.5, 25.0, 0.1, 0.0),
                                         copy.copy(Main_Pump),
                                         Pipe('MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
                                         Pipe('Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)],
                              slurry=base_slurry),
          }

try:
    import CustomSetups
    setups.update(CustomSetups.setups)
    pipeline = setups["Rudee II"]  # Update this with the pipeline setup you want to use
except ImportError:
    print('Import Error: Custom Dredge setups not found. To use, create file named CustomSetups.py with a dictionary '
          'named setups with dredge_name: Pipeline() items.')
    pipeline = setups["Example"]


pipeline.slurry.Dp = pipeline.pipesections[-1].diameter
pipeline.update_slurries()


def system_panel(PL):
    """Create a Bokeh Panel with the pipeline and an overall HQ plot"""

    flow_list = [pipeline.pipesections[-1].flow(v) for v in pipeline.slurry.vls_list]
    head_lists = list(zip(*[pipeline.calc_system_head(Q) for Q in flow_list]))
    im_source = ColumnDataSource(data=dict(Q=flow_list,
                                           v=pipeline.slurry.vls_list,
                                           im=head_lists[0],
                                           il=head_lists[1],
                                           Hpump_l = head_lists[2],
                                           Hpump_m = head_lists[3]))

    HQ_TOOLTIPS = [('name', "$name"),
                   ("Flow (m\u00b3/sec)", "@Q{0.00}"),
                   ("Velocity (m/sec)", "@v{0.00}"),
                   ("Slurry Graded Cvt=c (m)", "@im{0,0.0}"),
                   ("Fluid (m)", "@il{0,0.0}"),
                   ("Pump Head Slurry (m)", "@Hpump_m{0,0.0}",),
                   ("Pump Head Water (m)", "@Hpump_l{0,0.0}",),
                  ]
    HQ_plot = figure(height=450, width=725, title="System Head Requirement",
                     tools="crosshair,pan,reset,save,wheel_zoom",
                     #x_range=[0, 10], y_range=[0, 0.6],
                     tooltips=HQ_TOOLTIPS)

    HQ_plot.line('Q', 'im', source=im_source,
                 color='black',
                 line_dash='solid',
                 line_width=3,
                 line_alpha=0.6,
                 legend_label='Slurry Graded Cvt=c (m)',
                 name='Slurry graded Sand Cvt=c')

    HQ_plot.line('Q', 'il', source=im_source,
                 color='blue',
                 line_dash='solid',
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
    HQ_plot.xaxis[0].formatter=NumeralTickFormatter(format="0.0")
    HQ_plot.yaxis[0].axis_label = 'Head (m)'
    HQ_plot.y_range.end = 2 * pipeline.calc_system_head(0.1)[3]
    HQ_plot.axis.major_tick_in = 10
    HQ_plot.axis.minor_tick_in = 7
    HQ_plot.axis.minor_tick_out = 0
    HQ_plot.legend.location = "top_left"

    def update_all(pipeline):
        """Update the data sources and information boxes"""
        flow_list = [pipeline.pipesections[-1].flow(v) for v in pipeline.slurry.vls_list]
        head_lists = list(zip(*[pipeline.calc_system_head(Q) for Q in flow_list]))
        im_source.data=dict(Q=flow_list,
                            v=pipeline.slurry.vls_list,
                            im=head_lists[0],
                            il=head_lists[1],
                            Hpump_l = head_lists[2],
                            Hpump_m = head_lists[3])
        HQ_plot.xaxis[0].axis_label = f'Velocity (m/sec in {pipeline.slurry.Dp:0.3f}m pipe)'
        old_disch_dia = pipeline.pipesections[-1].diameter
        for p, pipe_row in zip(pipeline.pipesections, pipecol.children[1:]):
            if isinstance(p, Pipe) and p.diameter == old_disch_dia:
                pipe_row.children[2].value=f"{p.diameter:0.3f}"
        totalscol.children[0].children[2].value=f"{pipeline.pipesections[-1].diameter:0.3f}"
        update_opcol()

    def pipe_panel(i, pipe):
        """Create a Bokeh row with information about the pipe"""
        if isinstance(pipe, Pipe):
            return row(TextInput( value=f'{i:3d}', width=45),
                       TextInput(value=pipe.name, width=95),
                       TextInput(value=f"{pipe.diameter:0.3f}", width=76),
                       TextInput( value=f"{pipe.length:0.1f}", width=76),
                       TextInput( value=f"{pipe.total_K:0.2f}", width=76),
                       TextInput(value=f"{pipe.elev_change:0.1f}", width=76),)
        elif isinstance(pipe, Pump):
            return row(TextInput(title="#", value=f'{i:3d}', width=45, background='lightblue'),
                       TextInput(title="Pump", value=pipe.name, width=95, background='lightblue'),
                       TextInput(title="Suction (m)", value=f"{pipe.suction_dia:0.3f}", width=76, background='lightblue'),
                       TextInput(title="Discharge (m)", value=f"{pipe.disch_dia:0.3f}", width=76, background='lightblue'),
                       TextInput(title="Impeller (m)", value=f"{pipe.design_impeller:0.3f}", width=76, background='lightblue'),
                       TextInput(title="Power (kW)", value=f"{pipe.avail_power:0.0f}", width=76, background='lightblue'),)
        else:
            return row(TextInput(value="Unknown Item", width=76),)

    def pipeline_totals():
        """Create rows for totals in the pipeline"""
        pipe_totals = row(TextInput(title="#", value=f'{pipeline.num_pipesections:3d}', width=45, disabled=True),
                          TextInput(title="Pipe Sections", value="Total", width=95, disabled=True),
                          TextInput(title="Disch Dia (m)", value=f"{pipeline.pipesections[-1].diameter:0.3f}", width=76, disabled=True),
                          TextInput(title="Length (m)", value=f"{sum([pipeline.total_length]):0.1f}", width=76, disabled=True),
                          TextInput(title="Fitting K (-)", value=f"{pipeline.total_K:0.2f}", width=76, disabled=True),
                          TextInput(title="Delta z (m)", value=f"{pipeline.total_lift:0.1f}", width=76, disabled=True),)
        shutoff_head = pipeline.calc_system_head(0.01)
        pump_totals = row(TextInput(title="#", value=f'{pipeline.num_pumps:3d}', width=45, disabled=True),
                          TextInput(title="Pumps", value="Total", width=95, disabled=True),
                          TextInput(title="Head Water", value=f"{shutoff_head[2]:0.0f}", width=95, disabled=True),
                          TextInput(title="Head Slurry", value=f"{shutoff_head[3]:0.0f}", width=95, disabled=True),
                          TextInput(title="Power (kW)", value=f"{pipeline.total_power:0.0f}", width=95, disabled=True),)
        return column(pipe_totals, pump_totals)
    totalscol = pipeline_totals()

    pipecol = column(row(TextInput( value=f'#', width=45, disabled=True),
                         TextInput(value='name', width=95, disabled=True),
                         TextInput(value=f"diameter (m)", width=76, disabled=True),
                         TextInput( value=f"Length (m)", width=76, disabled=True),
                         TextInput( value=f"Total K", width=76, disabled=True),
                         TextInput(value=f"Delta z (m)", width=76, disabled=True),))
    [pipecol.children.append(pipe_panel(i, p)) for i, p in enumerate(pipeline.pipesections)]

    # Create textboxes with operating points
    qimin = pipeline.qimin(flow_list)
    try:
        qop = pipeline.find_operating_point(flow_list)
        qop_str = f'{qop:0.2f}'
        vop = f'{pipeline.pipesections[-1].velocity(qop):0.2f}'
        hop = f'{pipeline.calc_system_head(qop)[0]:0.1f}'
        prod = f'{pipeline.slurry.Cvi*qop*60*60:0.0f}'
    except ValueError:
        qop = qimin
        qop_str = "None"
        vop = "None"
        hop = "None"
        prod = "None"
    opcol = column(Spacer(background='lightblue', height=5, margin=(5, 0, 5, 0)),
                   Div(text="""<B>Minimum Slurry Friction Point</B>"""),
                   row(TextInput(title="Q (m\u00b3/sec)", value=f'{qimin:0.2f}', width=95, disabled=True),
                       TextInput(title="v\u2098 (m/sec)", value=f'{pipeline.pipesections[-1].velocity(qimin):0.2f}',
                                 width=95, disabled=True),
                       TextInput(title="H (m)", value=f'{pipeline.calc_system_head(qimin)[0]:0.1f}',
                                 width=95, disabled=True)
                       ),
                   Spacer(background='lightblue', height=5, margin=(5, 0, 5, 0)),
                   Div(text="""<B>Pump/Pipeline Slurry Operating Point</B>"""),
                   row(TextInput(title="Q (m\u00b3/sec)", value=qop_str, width=95, disabled=True),
                       TextInput(title="v\u2098 (m/sec)", value=vop,
                                 width=95, disabled=True),
                       TextInput(title="H (m)", value=hop,
                                 width=95, disabled=True),
                       TextInput(title="Production (m\u00b3/Hr)", value=prod,
                                 width=95, disabled=True)
                       )
                   )

    ###################################################################
    # The hydraulic gradeline plot
    hyd_TOOLTIPS = [('name', "$name"),
                   ("Location (m)", "@x{0.1}"),
                   ("Head (m)", "@h{0.1}"),
                   ]
    x, h = pipeline.hydraulic_gradient(qop)
    hyd_source = ColumnDataSource(data=dict(x=x,
                                            h=h))
    hyd_plot = figure(height=450, width=725, title="Hydraulic Gradeline",
                      tools="crosshair,pan,reset,save,wheel_zoom",
    tooltips= hyd_TOOLTIPS)

    hyd_plot.line('x', 'h', source=hyd_source,
                  color='black',
                  line_dash='solid',
                  line_width=3,
                  line_alpha=0.6,
                  legend_label='Hydraulic Gradeline slurry',
                  name='Hydraulic Gradeline slurry')
    hyd_plot.xaxis[0].axis_label = f'Location in pipeline (m)'
    hyd_plot.yaxis[0].axis_label = 'Head (m)'

    def update_opcol():
        """Update the operating point boxes"""
        qimin = pipeline.qimin(flow_list)
        imin_row = opcol.children[2].children
        imin_row[0].value = f'{qimin:0.2f}'
        imin_row[1].value = f'{pipeline.pipesections[-1].velocity(qimin):0.2f}'
        imin_row[2].value = f'{pipeline.calc_system_head(qimin)[0]:0.1f}'
        try:
            qop = pipeline.find_operating_point(flow_list)
            qop_str = f'{qop:0.2f}'
            vop = f'{pipeline.pipesections[-1].velocity(qop):0.2f}'
            hop = f'{pipeline.calc_system_head(qop)[0]:0.1f}'
            prod = f'{pipeline.slurry.Cvi * qop * 60 * 60:0.0f}'
        except ValueError:
            qop = qimin
            qop_str = "None"
            vop = "None"
            hop = "None"
            prod = "None"
        oppnt_row = opcol.children[5].children
        for i, op_str in enumerate([qop_str, vop, hop, prod]):
            oppnt_row[i].value = op_str
        X, H = pipeline.hydraulic_gradient(qop)
        hyd_source.data = dict(x=X,
                               h=H)

    return (Panel(title="Pipeline", child = row(column(totalscol,
                                                      Spacer(background='lightblue', height=5, margin=(5, 0, 5, 0)),
                                                      pipecol),
                                                Spacer(background='lightblue', width=5, margin=(0, 5, 0, 5)),
                                                column(HQ_plot,
                                                       opcol,
                                                       hyd_plot))),
            update_all)
