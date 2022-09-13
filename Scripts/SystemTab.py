"""
SystemTab: Create the tab with the system (pipeline and pumps) information, in SI or US units

Added by R. Ramsdell 01 September, 2021
"""
import copy

from DHLLDV.PipeObj import Pipeline, Pipe
from DHLLDV.PumpObj import Pump
from DHLLDV.SlurryObj import Slurry
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, HoverTool
from bokeh.models import Spacer, Panel, LinearAxis, Range1d, Div, NumeralTickFormatter, Dropdown
from bokeh.plotting import figure

from ExamplePumps import Ladder_Pump, Main_Pump, Ladder_Pump600, Main_Pump500, base_slurry

# Example of how to handle ladder pump elevations
# The ladder pump elev, and thus elev_change, varies with dig depth
dig_elev = -10      # Depths are positive down, elevations are positive up
ladder_length = 30
ladder_pump_location = 10
MP_elev = 1
LP_elev = dig_elev + ladder_pump_location * (MP_elev - dig_elev) / ladder_length


setups = {"CSD Example w/ Ladder Pump": Pipeline(name="CSD with Ladder Pump",
                                                 pipe_list=[Pipe(name='Entrance', diameter=0.85, length=0,
                                                                 total_K=0.5, elev_change=dig_elev),
                                                            Pipe('LP Suction', 0.86, ladder_pump_location, 0.1,
                                                                 LP_elev-dig_elev),
                                                            copy.copy(Ladder_Pump),
                                                            Pipe('LP Discharge', 0.86, ladder_length-ladder_pump_location,
                                                                 0.15, MP_elev-LP_elev),
                                                            Pipe('Hull Suction', 0.86, 6.0, 0.1, 0.0),
                                                            copy.copy(Main_Pump),
                                                            Pipe('MP Discharge', 0.762, 20.0, 0.2, -1.0),
                                                            Pipe('Discharge', 0.762, 2000.0, 1.0, 5.0)],
                                                 slurry=base_slurry),
          "Test Pipeline": Pipeline(name="test pipeline",
                                    pipe_list=[Pipe('Entrance', 0.6, 0, 0.5, -4.0),
                                               Pipe(diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0),
                                               Ladder_Pump600,
                                               Pipe('MP Suction', 0.5, 25.0, 0.1, 0.0),
                                               Main_Pump500,
                                               Pipe('MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
                                               Pipe('Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)],
                                    slurry=Slurry(Dp=0.5, fluid="salt"))
          }

try:
    import CustomSetups
    setups.update(CustomSetups.setups)
    pipeline = setups[CustomSetups.setup_to_use]
except ImportError:
    print('Import Error: Custom Dredge setups not found. To use, create file Scripts\CustomSetups.py with the following code:')
    print('''"""Custom setups for My Project"""

import copy

from DHLLDV.PipeObj import Pipeline, Pipe
from ExamplePumps import Ladder_Pump, Main_Pump, base_slurry

my_slurry = copy.deepcopy(base_slurry)
my_slurry.D50 = 0.4/1000    # Set the GSD to medium sand

setup_to_use = "My Dredge" # Update this with the pipeline setup you want shown at the start
setups = {"My Dredge": Pipeline(pipe_list=[Pipe('Entrance', 0.6, 0, 0.5, -4.0),
                                           Pipe(diameter=0.6, length=10.0, total_K=0.1, elev_change=5.0),
                                           copy.copy(Ladder_Pump),
                                           Pipe('MP Suction', 0.5, 25.0, 0.1, 0.0),
                                           copy.copy(Main_Pump),
                                           Pipe('MP Discharge', diameter=0.5, length=20.0, total_K=0.2, elev_change=-1.0),
                                           Pipe('Discharge', diameter=0.5, length=1000.0, total_K=1.0, elev_change=1.0)],
                                slurry=my_slurry),
          }''')
    pipeline = setups["Test Pipeline"]      # This is the pipeline from the tests


pipeline.slurry.Dp = pipeline.pipesections[-1].diameter
pipeline.update_slurries()

# Unit conversions
unit_conv_US = {'len': 1/0.3048,
                'dia': 12/0.3048,
                'vol': (1/.3048)**3/27,
                'flow': 15850.32,
                'power': 1/0.7457,
                'pressure': 1.42,
                'rot speed': 60}
unit_label_US = {'len': 'Ft',
                 'vel': 'Ft/sec',
                 'dia': 'In',
                 'vol': 'CY',
                 'flow': 'GPM',
                 'power': 'HP',
                 'pressure': 'psi',
                 'rot speed': 'RPM',}
unit_conv_SI = {v: 1.0 for v in unit_conv_US.keys()}
unit_conv_SI['rot speed'] = unit_conv_US['rot speed']
unit_conv_SI['dia'] = 1000
unit_conv_SI['pressure'] = 9.804139
unit_label_SI = {'len': 'm',
                 'vel': 'm/sec',
                 'dia': 'mm',
                 'vol': 'm\u00b3',
                 'flow': 'm\u00b3/sec',
                 'power': 'kW',
                 'pressure': 'kPa',
                 'rot speed': 'RPM',}

unit_convs = unit_conv_SI
unit_labels = unit_label_SI
def select_units(units='SI'):
    global unit_convs, unit_labels
    if units == 'US':
        unit_convs = unit_conv_US
        unit_labels = unit_label_US
    else:
        unit_convs = unit_conv_SI
        unit_labels = unit_label_SI


def convert_list(conversion, values):
    """Covert the values in a list using the given conversion"""
    return [v*conversion for v in values]


def system_panel(PL):
    """Create a Bokeh Panel with the pipeline and an overall HQ plot
    pipeline = PL

    Return a bokeh Panel and update function"""
    pipeline = PL

    flow_list = [pipeline.pipesections[-1].flow(v) for v in pipeline.slurry.vls_list]
    head_lists = list(zip(*[pipeline.calc_system_head(Q) for Q in flow_list]))
    im_source = ColumnDataSource(data=dict(Q=convert_list(unit_convs['flow'], flow_list),
                                           v=convert_list(unit_convs['len'], pipeline.slurry.vls_list),
                                           im=convert_list(unit_convs['len'], head_lists[0]),
                                           il=convert_list(unit_convs['len'], head_lists[1]),
                                           Hpump_l=convert_list(unit_convs['len'], head_lists[2]),
                                           Hpump_m=convert_list(unit_convs['len'], head_lists[3])))

    HQ_hover = HoverTool(tooltips =[('name', "$name"),
                                    (f"Flow ({unit_labels['flow']})", "@Q{0.00}"),
                                    (f"Velocity ({unit_labels['vel']})", "@v{0.0}"),
                                    (f"Slurry Graded Cvt=c ({unit_labels['len']})", "@im{0,0.0}"),
                                    (f"Fluid ({unit_labels['len']})", "@il{0,0.0}"),
                                    (f"Pump Head Slurry ({unit_labels['len']})", "@Hpump_m{0,0.0}",),
                                    (f"Pump Head Water ({unit_labels['len']})", "@Hpump_l{0,0.0}",),
                                    ])
    HQ_plot = figure(height=450, width=595, title="System Head Requirement",
                     tools="crosshair,pan,reset,save,wheel_zoom",
                     x_range=[0, flow_list[-1]*unit_convs['flow']], y_range=[0, 100])
    HQ_plot.tools.append(HQ_hover)

    HQ_plot.line('Q', 'im', source=im_source,
                 color='black',
                 line_dash='solid',
                 line_width=3,
                 line_alpha=0.6,
                 legend_label=f'Slurry Graded Cvt=c ({unit_labels["len"]})',
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
    HQ_plot.extra_x_ranges = {'vel_range': Range1d(pipeline.slurry.vls_list[0]*unit_convs['len'], pipeline.slurry.vls_list[-1]*unit_convs['len'])}
    HQ_plot.add_layout(LinearAxis(x_range_name='vel_range'), 'above')
    HQ_plot.xaxis[1].axis_label = f'Flow ({unit_labels["flow"]})'
    HQ_plot.xaxis[0].axis_label = f'Velocity ({unit_labels["vel"]} in {pipeline.slurry.Dp*unit_convs["dia"]:0.1f} {unit_labels["dia"]} pipe)'
    HQ_plot.xaxis[0].formatter=NumeralTickFormatter(format="0.0")
    HQ_plot.yaxis[0].axis_label = f'Head ({unit_labels["len"]})'
    HQ_plot.y_range.end = 2 * pipeline.calc_system_head(0.1)[3]*unit_convs['len']
    HQ_plot.axis.major_tick_in = 10
    HQ_plot.axis.minor_tick_in = 7
    HQ_plot.axis.minor_tick_out = 0
    HQ_plot.legend.location = "top_left"

    def update_all(pipeline):
        """Update the data sources and information boxes"""
        this_pipe = Pipe(diameter=pipeline.slurry.Dp)
        flow_list = [this_pipe.flow(v) for v in pipeline.slurry.vls_list]
        head_lists = list(zip(*[pipeline.calc_system_head(Q) for Q in flow_list]))
        im_source.data=dict(Q=convert_list(unit_convs['flow'], flow_list),
                                           v=convert_list(unit_convs['len'], pipeline.slurry.vls_list),
                                           im=convert_list(unit_convs['len'], head_lists[0]),
                                           il=convert_list(unit_convs['len'], head_lists[1]),
                                           Hpump_l=convert_list(unit_convs['len'], head_lists[2]),
                                           Hpump_m=convert_list(unit_convs['len'], head_lists[3]))
        HQ_plot.xaxis[1].axis_label = f'Flow ({unit_labels["flow"]})'
        HQ_plot.xaxis[0].axis_label = f'Velocity ({unit_labels["vel"]} in {pipeline.slurry.Dp*unit_convs["dia"]:0.1f} {unit_labels["dia"]} pipe)'
        HQ_plot.x_range.end=flow_list[-1]*unit_convs['flow']
        HQ_plot.extra_x_ranges['vel_range'].end = pipeline.slurry.vls_list[-1]*unit_convs['len']
        HQ_plot.y_range.end = 2 * pipeline.calc_system_head(0.1)[3]*unit_convs['len']
        HQ_plot.yaxis[0].axis_label = f'Head ({unit_labels["len"]})'
        HQ_plot.tools[5].tooltips = [('name', "$name"),
                                     (f"Flow ({unit_labels['flow']})", "@Q{0.00}"),
                                     (f"Velocity ({unit_labels['vel']})", "@v{0.0}"),
                                     (f"Slurry Graded Cvt=c ({unit_labels['len']})", "@im{0,0.0}"),
                                     (f"Fluid ({unit_labels['len']})", "@il{0,0.0}"),
                                     (f"Pump Head Slurry ({unit_labels['len']})", "@Hpump_m{0,0.0}",),
                                     (f"Pump Head Water ({unit_labels['len']})", "@Hpump_l{0,0.0}",),
                                     ]

        # Update the pipeline columns
        del totalscol.children[:]
        totalscol.children.extend(pipeline_totals(pipeline).children)
        del pipecol.children[1:]
        [pipecol.children.append(pipe_panel(pipeline, i)) for i, p in enumerate(pipeline.pipesections)]

        update_opcol(pipeline)
        slurry_info.text = f'{pipeline.slurry}'.replace('\n', '<BR>')

    def pipe_panel(pipeline, i):
        """Create a Bokeh row with information about the pipe"""
        pipe = pipeline.pipesections[i]
        if isinstance(pipe, Pipe):
            return row(TextInput( value=f'{i:3d}', width=45),
                       TextInput(value=pipe.name, width=150),
                       TextInput(value=f"{pipe.diameter*unit_convs['dia']:0.1f}", width=76),
                       TextInput( value=f"{pipe.length*unit_convs['len']:0.0f}", width=76),
                       TextInput( value=f"{pipe.total_K:0.2f}", width=76),
                       TextInput(value=f"{pipe.elev_change*unit_convs['len']:0.1f}", width=76),)
        elif isinstance(pipe, Pump):
            num = TextInput(title="#", value=f'{i:3d}', width=45, background='lightblue')
            row1 = row(TextInput(title="Pump", value=pipe.name, width=150, background='lightblue'),
                       TextInput(title=f"Suction ({unit_labels['dia']})", value=f"{pipe.suction_dia*unit_convs['dia']:0.1f}", width=76, background='lightblue'),
                       TextInput(title=f"Discharge ({unit_labels['dia']})", value=f"{pipe.disch_dia*unit_convs['dia']:0.1f}", width=76, background='lightblue'),
                       TextInput(title=f"Impeller ({unit_labels['dia']})", value=f"{pipe.design_impeller*unit_convs['dia']:0.1f}", width=76, background='lightblue'),
                       TextInput(title=f"Power ({unit_labels['power']})", value=f"{pipe.avail_power*unit_convs['power']:0.0f}", width=76, background='lightblue'),)
            flow_pipe = Pipe(diameter=pipeline.slurry.Dp)
            flow_list = [flow_pipe.flow(v) for v in pipeline.slurry.vls_list]
            qop = pipeline.find_operating_point(flow_list)
            if qop > 0:
                locs, heads, _ = pipeline.hydraulic_gradient(qop)
                _, _, P, n = pipe.point(qop)
                op_suction = f"{heads[i]*unit_convs['pressure']:0.1f}"
                op_discharge = f"{heads[i+1]*unit_convs['pressure']:0.1f}"
                op_power = f"{P*unit_convs['power']:0.0f}"
                op_speed = f"{n * unit_convs['rot speed']:0.0f}"
            else:
                op_suction = f"N/A"
                op_discharge = f"N/A"
                op_power = f"N/A"
                op_speed = f"N/A"

            # print(f"SystemTab.pipe_panel: pump: {pipe.name} qop:{qop:0.3f} power: {P:0.0f} n:{n:0.3f}")
            row2 = row(TextInput(title="", value="At Operating Point:", width=150, background='lightblue'),
                       TextInput(title=f"Suction ({unit_labels['pressure']})",
                                 value=op_suction,
                                 width=76, background='lightblue'),
                       TextInput(title=f"Discharge ({unit_labels['pressure']})",
                                 value=op_discharge,
                                 width=76, background='lightblue'),
                       TextInput(title=f"Speed ({unit_labels['rot speed']})",
                                 value=op_speed,
                                 width=76, background='lightblue'),
                       TextInput(title=f"Power ({unit_labels['power']})",
                                 value=op_power,
                                 width=76, background='lightblue'),)
            return row(num, column(row1, row2))
        else:
            return row(TextInput(value="Unknown Item", width=76),)

    def pipeline_totals(pipeline):
        """Create rows for totals in the pipeline"""
        if pipeline.pipesections[0].length > 0:
            dig_depth = 0
            lift = pipeline.total_lift
        else:
            dig_depth = pipeline.pipesections[0].elev_change
            lift = pipeline.total_lift - dig_depth
        pipe_totals = row(TextInput(title="#", value=f'{pipeline.num_pipesections:3d}', width=45, disabled=True),
                          TextInput(title="Pipe Sections", value="Total", width=150, disabled=True),
                          TextInput(title=f"Disch Dia ({unit_labels['dia']})", value=f"{pipeline.pipesections[-1].diameter*unit_convs['dia']:0.1f}", width=76, disabled=True),
                          TextInput(title=f"Length ({unit_labels['len']})", value=f"{pipeline.total_length*unit_convs['len']:0.0f}", width=76, disabled=True),
                          TextInput(title="Fitting K (-)", value=f"{pipeline.total_K:0.2f}", width=76, disabled=True),
                          TextInput(title=f"Delta z ({unit_labels['len']})", value=f"{lift*unit_convs['len']:0.1f}", width=76, disabled=True),)
        elevations = row(TextInput(title=f"Dig Depth ({unit_labels['len']})", value=f"{dig_depth*unit_convs['len']:0.1f}", width=100, disabled=True),
                         TextInput(title=f"Discharge Elevation ({unit_labels['len']})", value=f"{pipeline.total_lift * unit_convs['len']:0.1f}", width=100, disabled=True))
        shutoff_head = pipeline.calc_system_head(0.01)
        pump_totals = row(TextInput(title="#", value=f'{pipeline.num_pumps:3d}', width=45, disabled=True),
                          TextInput(title="Pumps", value="Total", width=150, disabled=True),
                          TextInput(title="Head Water", value=f"{shutoff_head[2]*unit_convs['len']:0.0f}", width=95, disabled=True),
                          TextInput(title="Head Slurry", value=f"{shutoff_head[3]*unit_convs['len']:0.0f}", width=95, disabled=True),
                          TextInput(title=f"Power ({unit_labels['power']})", value=f"{pipeline.total_power*unit_convs['power']:0.0f}", width=95, disabled=True),)
        return column(pipe_totals, elevations, pump_totals)
    totalscol = pipeline_totals(pipeline)

    pipecol = column(row(TextInput( value=f'#', width=45, disabled=True),
                         TextInput(value='name', width=150, disabled=True),
                         TextInput(value=f"diameter ({unit_labels['dia']})", width=76, disabled=True),
                         TextInput( value=f"Length ({unit_labels['len']})", width=76, disabled=True),
                         TextInput( value=f"Total K", width=76, disabled=True),
                         TextInput(value=f"Delta z ({unit_labels['len']})", width=76, disabled=True),))
    [pipecol.children.append(pipe_panel(pipeline, i)) for i, p in enumerate(pipeline.pipesections)]

    # Create textboxes with operating points
    qimin = pipeline.qimin(flow_list)
    try:
        qop = pipeline.find_operating_point(flow_list)
        qop_str = f'{qop*unit_convs["flow"]:0.2f}'
        vop = f'{pipeline.pipesections[-1].velocity(qop)*unit_convs["len"]:0.1f}'
        hop = f'{pipeline.calc_system_head(qop)[0]*unit_convs["len"]:0.1f}'
        prod = f'{pipeline.slurry.Cvi*qop*60*60*unit_convs["vol"]:0.0f}'
    except ZeroDivisionError:
        qop = qimin
        qop_str = "None"
        vop = "None"
        hop = "None"
        prod = "None"
    opcol = column(Spacer(background='lightblue', height=5, margin=(5, 0, 5, 0)),
                   Div(text="""<B>Minimum Slurry Friction Point</B>"""),
                   row(TextInput(title=f"Q {unit_labels['flow']}", value=f'{qimin*unit_convs["flow"]:0.2f}', width=95, disabled=True),
                       TextInput(title=f"v\u2098 ({unit_labels['vel']})", value=f'{pipeline.pipesections[-1].velocity(qimin)*unit_convs["len"]:0.1f}',
                                 width=95, disabled=True),
                       TextInput(title=f"H ({unit_labels['len']})", value=f'{pipeline.calc_system_head(qimin)[0]*unit_convs["len"]:0.1f}',
                                 width=95, disabled=True)
                       ),
                   Spacer(background='lightblue', height=5, margin=(5, 0, 5, 0)),
                   Div(text="""<B>Pump/Pipeline Slurry Operating Point</B>"""),
                   row(TextInput(title=f"Q ({unit_labels['flow']})", value=qop_str, width=95, disabled=True),
                       TextInput(title=f"v\u2098 ({unit_labels['vel']})", value=vop,
                                 width=95, disabled=True),
                       TextInput(title=f"H ({unit_labels['len']})", value=hop,
                                 width=95, disabled=True),
                       TextInput(title=f"Production ({unit_labels['vol']}/Hr)", value=prod,
                                 width=95, disabled=True)
                       ),
                   Spacer(background='lightblue', height=5, margin=(5, 0, 5, 0))
                   )

    ###################################################################
    # The hydraulic gradeline plot
    hyd_hover = HoverTool(tooltips=[('name', "$name"),
                                    ('Section:', "@names"),
                                    (f"Location ({unit_labels['len']})", "@x{0.0}"),
                                    (f"Elevation ({unit_labels['len']})", "@e{0.0}"),
                                    (f"Pressure ({unit_labels['pressure']})", "@h{0.1}"),
                                    ])
    x, h, e = pipeline.hydraulic_gradient(qop)
    pipe_names = [f'Pipe: {p.name}' if isinstance(p, Pipe) else f'Pump: {p.name}' for p in pipeline.pipesections]
    pipe_names.insert(0, 'Entrance')

    hyd_source = ColumnDataSource(data=dict(x=convert_list(unit_convs['len'], x),
                                            e=convert_list(unit_convs['len'], e),
                                            h=convert_list(unit_convs['pressure'], h),
                                            names=pipe_names))
    hyd_plot = figure(height=330, width=595, title="Pressure Gradeline",
                      tools="crosshair,pan,reset,save,wheel_zoom",
                      y_range=(min(h)*unit_convs['pressure'], max(h)*unit_convs['pressure']*1.01),
                      x_range=(min(x)*unit_convs['len'], max(x)*unit_convs['len']))
    hyd_plot.tools.append(hyd_hover)
    hyd_plot.xaxis[0].axis_label = f'Location in pipeline ({unit_labels["len"]})'
    hyd_plot.yaxis[0].axis_label = f'Pressure ({unit_labels["pressure"]})'

    hyd_plot.line('x', 'h', source=hyd_source,
                  color='black',
                  line_dash='solid',
                  line_width=3,
                  line_alpha=0.6,
                  legend_label='Pressure Gradeline slurry',
                  name='Pressure Gradeline slurry')

    hyd_plot.extra_y_ranges = {"e": Range1d(start=min(e), end=max(e)+(max(e)-min(e))*2)}
    second_hyd_y_axis = LinearAxis(y_range_name="e")
    hyd_plot.add_layout(second_hyd_y_axis, 'right')
    hyd_plot.yaxis[1].axis_label = f"Elevation ({unit_labels['len']})"
    hyd_plot.line('x', 'e', source=hyd_source,
                  y_range_name='e',
                  color='green',
                  line_dash='solid',
                  line_width=3,
                  line_alpha=0.6,
                  legend_label='Pipeline Elevations',
                  name='Pipeline Elevations')


    def update_opcol(pipeline):
        """Update the operating point boxes"""
        qimin = pipeline.qimin(flow_list)
        imin_row = opcol.children[2].children
        imin_row[0].title = f"Q ({unit_labels['flow']})"
        imin_row[0].value = f'{qimin*unit_convs["flow"]:0.2f}'
        imin_row[1].title = f"v\u2098 ({unit_labels['vel']})"
        imin_row[1].value = f'{pipeline.pipesections[-1].velocity(qimin)*unit_convs["len"]:0.1f}'
        imin_row[2].title = f"H ({unit_labels['len']})"
        imin_row[2].value = f'{pipeline.calc_system_head(qimin)[0]*unit_convs["len"]:0.1f}'
        try:
            qop = pipeline.find_operating_point(flow_list)
            qop_str = f'{qop*unit_convs["flow"]:0.2f}'
            vop = f'{pipeline.pipesections[-1].velocity(qop)*unit_convs["len"]:0.1f}'
            hop = f'{pipeline.calc_system_head(qop)[0]*unit_convs["len"]:0.1f}'
            prod = f'{pipeline.slurry.Cvi * qop * 60 * 60 * unit_convs["vol"]:0.0f}'
        except ZeroDivisionError:
            qop = qimin
            qop_str = "None"
            vop = "None"
            hop = "None"
            prod = "None"
        oppnt_row = opcol.children[5].children
        for i, op_str in enumerate([qop_str, vop, hop, prod]):
            oppnt_row[i].value = op_str
        for i, op_label in enumerate([f"Q ({unit_labels['flow']})",
                                      f"v\u2098 ({unit_labels['vel']})",
                                      f"H ({unit_labels['len']})",
                                      f"Production ({unit_labels['vol']}/Hr)",]):
            oppnt_row[i].title = op_label
        x, h, e = pipeline.hydraulic_gradient(qop)
        pipe_names = [f'Pipe: {p.name}' if isinstance(p, Pipe) else f'Pump: {p.name}' for p in pipeline.pipesections]
        pipe_names.insert(0, 'Entrance')
        hyd_source.data = dict(x=convert_list(unit_convs['len'], x),
                               e=convert_list(unit_convs['len'], e),
                               h=convert_list(unit_convs['pressure'], h),
                               names=pipe_names)
        hyd_plot.xaxis[0].axis_label = f'Location in pipeline ({unit_labels["len"]})'
        hyd_plot.x_range.start = min(x) * unit_convs['len']
        hyd_plot.x_range.end = max(x) * unit_convs['len']
        hyd_plot.yaxis[0].axis_label = f'Pressure ({unit_labels["pressure"]})'
        hyd_plot.y_range.start = min(h) * unit_convs['pressure']
        hyd_plot.y_range.end = max(h) * unit_convs['pressure']*1.01
        hyd_plot.yaxis[1].axis_label = f"Elevation ({unit_labels['len']})"
        hyd_plot.extra_y_ranges['e'].start = min(e) * unit_convs['len']
        hyd_plot.extra_y_ranges['e'].end = (max(e) + (max(e) - min(e)) * 2) * unit_convs['len']
        hyd_plot.tools[5].tooltips = [('name', "$name"),
                                      ('Section:', "@names"),
                                      (f"Location ({unit_labels['len']})", "@x{0.0}"),
                                      (f"Elevation ({unit_labels['len']})", "@e{0.0}"),
                                      (f"Pressure ({unit_labels['pressure']})", "@h{0.1}"),
                                      ]


    slurry_info = Div(text=f'{pipeline.slurry}'.replace('\n', '<BR>'))

    return (Panel(title="Pipeline US", child = row(column(totalscol,
                                                          Spacer(background='lightblue', height=5, margin=(5, 0, 5, 0)),
                                                          pipecol,
                                                          Spacer(background='lightblue', height=5, margin=(5, 0, 5, 0)),
                                                          slurry_info),
                                                   Spacer(background='lightblue', width=5, margin=(0, 5, 0, 5)),
                                                   column(HQ_plot,
                                                          opcol,
                                                          hyd_plot))),
            update_all)
