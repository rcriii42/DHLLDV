"""
bokeh_viewer: a program to view the curves in a bokeh interactive session

Execute by running 'bokeh serve --show .\Scripts\bokeh_viewer.py' to open a tab in your browser

Added by R. Ramsdell 19 August, 2021
"""
import sys

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Button, RadioButtonGroup
from bokeh.models import Spacer, Div, Panel, Tabs
from bokeh.models.tickers import FixedTicker
from bokeh.plotting import figure


from DHLLDV import DHLLDV_framework
from DHLLDV import PipeObj

import SystemTab

# Set up data

pipeline = SystemTab.pipeline
slurry = pipeline.slurry

im_source = ColumnDataSource(data=dict(v=slurry.vls_list,
                                       graded_Cvt_im=slurry.im_curves['graded_Cvt_im'],
                                       Cvs_im=slurry.im_curves['Cvs_im'],
                                       Cvt_im=slurry.im_curves['Cvt_im'],
                                       il=slurry.im_curves['il'],
                                       regime=slurry.Erhg_curves['Cvs_regime']))
LDV50_source = ColumnDataSource(data=dict(v=slurry.LDV_curves['vls'],
                                          im=slurry.LDV_curves['im'],
                                          il=slurry.LDV_curves['il'],
                                          Erhg=slurry.LDV_curves['Erhg'],
                                          regime=slurry.LDV_curves['regime']))
LDV85_source = ColumnDataSource(data=dict(v=slurry.LDV85_curves['vls'],
                                          im=slurry.LDV85_curves['im'],
                                          il=slurry.LDV85_curves['il'],
                                          Erhg=slurry.LDV85_curves['Erhg'],
                                          regime=slurry.LDV85_curves['regime']))
Erhg_source = ColumnDataSource(data=dict(il=slurry.Erhg_curves['il'],
                                         graded_Cvt=slurry.Erhg_curves['graded_Cvt_Erhg'],
                                         Cvs=slurry.Erhg_curves['Cvs_Erhg'],
                                         Cvt=slurry.Erhg_curves['Cvt_Erhg'],
                                         regime=slurry.Erhg_curves['Cvs_regime']))

def update_source_data():
    slurry.generate_curves()
    im_source.data = dict(v=slurry.vls_list,
                          graded_Cvt_im=slurry.im_curves['graded_Cvt_im'],
                          Cvs_im=slurry.im_curves['Cvs_im'],
                          Cvt_im=slurry.im_curves['Cvt_im'],
                          il=slurry.im_curves['il'],
                          regime=slurry.Erhg_curves['Cvs_regime'])
    LDV50_source.data = dict(v=slurry.LDV_curves['vls'],
                             im=slurry.LDV_curves['im'],
                             il=slurry.LDV_curves['il'],
                             Erhg=slurry.LDV_curves['Erhg'],
                             regime=slurry.LDV_curves['regime'])
    LDV85_source.data = dict(v=slurry.LDV85_curves['vls'],
                             im=slurry.LDV85_curves['im'],
                             il=slurry.LDV85_curves['il'],
                             Erhg=slurry.LDV85_curves['Erhg'],
                             regime=slurry.LDV85_curves['regime'])
    Erhg_source.data = dict(il=slurry.Erhg_curves['il'],
                            graded_Cvt=slurry.Erhg_curves['graded_Cvt_Erhg'],
                            Cvs=slurry.Erhg_curves['Cvs_Erhg'],
                            Cvt=slurry.Erhg_curves['Cvt_Erhg'],
                            regime=slurry.Erhg_curves['Cvs_regime'])
    roughness_label.value = f"{slurry.epsilon:0.3e}"
    fluid_viscosity_label.value = f"{slurry.nu:0.4e}"
    fluid_density_label.value = f"{slurry.rhol:0.4f}"
    Cvi_input.title = f'Cvi (\u03C1\u1D62 = {slurry.rhoi:0.3f})'
    Cvi_input.value = f"{slurry.Cvi:0.3f}"
    Rsd_input.value=f"{slurry.Rsd:0.3f}"
    rhom_input.value = f"{slurry.rhom:0.3f}"
    percents = sorted(list(slurry.GSD.keys()))
    GSD_source.data = dict(p=percents, dia=[slurry.GSD[pct] * 1000 for pct in percents])
    HQ_plot.xaxis[0].axis_label = f'Velocity (m/sec in {slurry.Dp:0.3f}m pipe)'
    sys_update(pipeline)

################
# Set up HQ plot
HQ_TOOLTIPS = [
    ('name', "$name"),
    ("vls (m/sec)", "@v"),
    ("Graded Cvt=c (m/m)", "@graded_Cvt_im"),
    ("Uniform Cvt=c", "@Cvt_im"),
    ("Uniform Cvs=c", "@Cvs_im"),
    ("Fluid", "@il"),
    ("Regime", "@regime")
]
HQ_plot = figure(height=450, width=725, title="im curves",
                 tools="crosshair,pan,reset,save,wheel_zoom",
                 #x_range=[0, 10], y_range=[0, 0.6],
                 tooltips=HQ_TOOLTIPS)

HQ_plot.line('v', 'graded_Cvt_im', source=im_source,
             color='black',
             line_dash='dashed',
             line_width=3,
             line_alpha=0.6,
             legend_label='graded Sand Cvt=c',
             name='graded Sand Cvt=c')

HQ_plot.line('v', 'Cvt_im', source=im_source,
             color='green',
             line_dash='dashed',
             line_width=2,
             line_alpha=0.6,
             legend_label='uniform Sand Cvt=c',
             name='uniform Sand Cvt=c')

HQ_plot.line('v', 'Cvs_im', source=im_source,
             color='red',
             line_dash='solid',
             line_width=2,
             line_alpha=0.6,
             legend_label='uniform Sand Cvs=c',
             name='uniform Sand Cvs=c')

HQ_plot.line('v', 'il', source=im_source,
             color='blue',
             line_dash='dashed',
             line_width=2,
             line_alpha=0.3,
             legend_label='il',
             name='il')

HQ_plot.line('v', 'im', source=LDV50_source,
             color='magenta',
             line_dash='solid',
             line_width=2,
             line_alpha=0.6,
             legend_label='LDV D50',
             name='LDV D50')
HQ_plot.line('v', 'im', source=LDV85_source,
             color='magenta',
             line_dash='dashed',
             line_width=1,
             line_alpha=0.6,
             legend_label='LDV D85',
             name='LDV D85')

HQ_plot.xaxis[0].axis_label = f'Velocity (m/sec in {slurry.Dp:0.3f}m pipe)'
HQ_plot.yaxis[0].axis_label = 'Head (m/m)'
HQ_plot.axis.major_tick_in = 10
HQ_plot.axis.minor_tick_in = 7
HQ_plot.axis.minor_tick_out = 0
HQ_plot.legend.location = "top_left"

######
# Set up Erhg Plot
Erhg_TOOLTIPS = [
    ('name', "$name"),
    ("il (m/m", "$x"),
    ("Erhg (-)", "$y"),
    ("Regime", "@regime")
]
Erhg_plot = figure(height=450, width=725, title="Erhg Curves",
                 tools="crosshair,pan,reset,save,wheel_zoom",
                 #x_range=[0.001, 1.0], y_range=[0.001, 1.2],
                 x_axis_type='log', y_axis_type='log',
                 tooltips=Erhg_TOOLTIPS)

Erhg_plot.line('il', 'graded_Cvt', source=Erhg_source,
             color='black',
             line_dash='dashed',
             line_width=3,
             line_alpha=0.6,
             legend_label='graded Sand Cvt=c',
             name='graded Sand Cvt=c')

Erhg_plot.line('il', 'Cvt', source=Erhg_source,
             color='green',
             line_dash='dashed',
             line_width=2,
             line_alpha=0.6,
             legend_label='uniform Sand Cvt=c',
             name='uniform Sand Cvt=c')

Erhg_plot.line('il', 'Cvs', source=Erhg_source,
             color='red',
             line_dash='solid',
             line_width=2,
             line_alpha=0.6,
             legend_label='uniform Sand Cvs=c',
             name='uniform Sand Cvs=c')

Erhg_plot.line('il', 'il', source=Erhg_source,
             color='blue',
             line_dash='dashed',
             line_width=2,
             line_alpha=0.3,
             legend_label='il',
             name='il')

Erhg_plot.line('il', 'Erhg', source=LDV50_source,
             color='magenta',
             line_dash='solid',
             line_width=2,
             line_alpha=0.6,
             legend_label='LDV D50',
             name='LDV D50')
Erhg_plot.line('il', 'Erhg', source=LDV85_source,
             color='magenta',
             line_dash='dashed',
             line_width=1,
             line_alpha=0.6,
             legend_label='LDV D85',
             name='LDV D85')

Erhg_plot.xaxis[0].axis_label = 'Hydraulic Gradient il (m/m)'
Erhg_plot.yaxis[0].axis_label = 'Relative Excess Hydraulic Gradient Erhg (-)'
Erhg_plot.axis.major_tick_in = 10
Erhg_plot.axis.minor_tick_in = 7
Erhg_plot.axis.minor_tick_out = 0
Erhg_plot.legend.location = "top_left"

######
# Set up GSD Plot
percents = sorted(list(slurry.GSD.keys()))
GSD_source = ColumnDataSource(data=dict(p=percents,
                                        dia=[slurry.GSD[pct]*1000 for pct in percents]))

GSD_TOOLTIPS = [
    ("Dia", "$x"),
    ("%", "$y"),
]
GSD_plot = figure(height=280, width=450, title="Grain Size Distribution",
                 tools="crosshair,pan,reset,save,wheel_zoom",
                 x_range=[0.0001, 1000], y_range=[0, 1.0],
                 x_axis_type='log', y_axis_type='auto',
                 tooltips=GSD_TOOLTIPS)

GSD_plot.line('dia', 'p', source=GSD_source,
             color='blue',
             line_dash='solid',
             line_width=1,
             line_alpha=0.6,
             #legend_label='Grain Size Distribution',
             name='GSD')

GSD_plot.circle_dot('dia', 'p', source=GSD_source, name='GSD')
GSD_plot.xaxis[0].axis_label = 'Grain Size (mm)'

GSD_plot.yaxis[0].axis_label = '% passing'
GSD_plot.yaxis.ticker = FixedTicker(ticks=[x*0.2 for x in range(5)],
                                    minor_ticks=[x*.05 for x in range(1, 20)])
GSD_plot.axis.major_tick_in = 10
GSD_plot.axis.minor_tick_in = 7
GSD_plot.axis.minor_tick_out = 0
GSD_plot.xgrid.minor_grid_line_color='navy'
GSD_plot.xgrid.minor_grid_line_alpha=0.1

# Set up widgets
def update_Dp(attrname, old, new):
    """Update the pipe diameter"""
    old_Dp = slurry.Dp
    slurry.Dp = check_value(Dp_input, 25, 1500, slurry.Dp * 1000, '0.0f') / 1000
    for p in pipeline.pipesections:
        if isinstance(p, PipeObj.Pipe) and p.diameter == old_Dp:
            p.diameter = slurry.Dp
    pipeline.update_slurries()
    update_source_data()

def Dp_up_callback():
    Dp_input.value=f"{int(slurry.Dp*1000)+25}"
def Dp_down_callback():
    Dp_input.value=f"{int(slurry.Dp*1000)-25}"
Dp_up_button = Button(label=u"\u25B2", width_policy="min", height_policy="min")
Dp_up_button.on_click(Dp_up_callback)
Dp_down_button = Button(label=u"\u25BC", width_policy="min", height_policy="min")
Dp_down_button.on_click(Dp_down_callback)
Dp_updown = column(Dp_up_button, Dp_down_button)
Dp_input = TextInput(title="Dp (mm)", value=f"{int(slurry.Dp*1000)}", width=95)
Dp_input.on_change('value', update_Dp)
roughness_label = TextInput(title="Roughness (m)", value=f"{slurry.epsilon:0.3e}",
                            width=95, disabled=True)
Dp_row = row(Dp_input, Dp_updown, Spacer(width=10), roughness_label)

def update_fluid(index):
    if index == 0:
        slurry.fluid = 'fresh'
    else:
        slurry.fluid = 'salt'
    update_source_data()

fluid_radio = RadioButtonGroup(labels=['Fresh', 'Salt'], active=1)
fluid_radio.on_click(update_fluid)
fluid_viscosity_label = TextInput(title=f"Viscosity \u03BD\u2097 (m\u00b2/sec)", value=f"{slurry.nu:0.4e}",
                                  width=125, disabled=True)
fluid_density_label = TextInput(title=f"Density \u03C1\u2097 (ton/m\u00b3)", value=f"{slurry.rhol:0.4f}",
                                width=125, disabled=True)
fluid_properties = row(fluid_viscosity_label, fluid_density_label)

def D50_adjust_proportionate(delta):
    """Adjust the D15 and D85 proportionately when D50 up/down buttons used"""
    if DHLLDV_framework.pseudo_dlim(slurry.Dp, slurry.nu, slurry.rhol, slurry.rhos)*1000 <\
            slurry.D50*1000 + delta <=\
            slurry.Dp * 1000 * 0.25:
        D85_input.remove_on_change('value', update_data)
        D50_input.remove_on_change('value', update_data)
        D15_input.remove_on_change('value', update_data)
        slurry.D50 += delta / 1000
        D15_ratio = slurry.get_dx(0.50) / slurry.get_dx(0.15)
        if slurry.D50 / D15_ratio < 0.08/1000:
            D15_ratio = slurry.D50 / (0.08/1000)
        D85_ratio = slurry.get_dx(0.85) / slurry.get_dx(0.50)
        slurry.generate_GSD(D15_ratio, D85_ratio)
        update_source_data()
        D85_input.value = f"{slurry.get_dx(0.85) * 1000:0.3f}"
        D50_input.value = f"{slurry.get_dx(0.50) * 1000:0.3f}"
        D15_input.value = f"{slurry.get_dx(0.15) * 1000:0.3f}"

        D15_input.on_change('value', update_data)
        D50_input.on_change('value', update_data)
        D85_input.on_change('value', update_data)

def D50_up_callback():
    D50_adjust_proportionate(0.1)
def D50_down_callback():
    D50_adjust_proportionate(-0.1)

def update_silt(attrname, old, new):
    if silt_input.value == '':
        slurry.silt = None
    else:
        slurry.silt = check_value(silt_input, 0.0, 49.99, slurry.silt, '0.1f') / 100
    slurry.generate_GSD(d15_ratio=slurry.D50 / slurry.get_dx(0.15), d85_ratio=slurry.get_dx(0.85) / slurry.D50)
    update_source_data()


D85_input = TextInput(title="D85 (mm)", value=f"{slurry.get_dx(0.85) * 1000:0.3f}", width=95)
D50_input = TextInput(title="D50 (mm)", value=f"{slurry.D50 * 1000:0.3f}", width=95)
D50_up_button = Button(label=u"\u25B2", width_policy="min", height_policy="min")
D50_up_button.on_click(D50_up_callback)
D50_down_button = Button(label=u"\u25BC", width_policy="min", height_policy="min")
D50_down_button.on_click(D50_down_callback)
D15_input = TextInput(title="D15 (mm)", value=f"{slurry.get_dx(0.15) * 1000:0.3f}", width=95)
silt_input = TextInput(title="% of 0.075 mm", value="", width=95)
silt_input.on_change('value', update_silt)

D50_updown = column(D50_up_button, D50_down_button)
GSD_inputs = row(D85_input, D50_input, D50_updown, Spacer(width=10), D15_input, silt_input)

def update_rhos(attrname, old, new):
    Cvi = (slurry.rhoi - slurry.rhol) / (slurry.rhos - slurry.rhol)
    slurry.rhos = check_value(rhos_input, 1.5, 7.0, slurry.rhos, "0.3f")
    slurry.rhoi = Cvi *(slurry.rhos - slurry.rhol) + slurry.rhol
    update_source_data()

rhos_input = TextInput(title="Solids Density \u03C1\u209B (ton/m\u00b3)", value=f"{slurry.rhos:0.3f}", width=150)
rhos_input.on_change('value', update_rhos)
Rsd_input = TextInput(title="Rsd (-)", value=f"{slurry.Rsd:0.3f}", disabled=True, width=95)
rhos_row = row(rhos_input, Rsd_input)

def update_rhom(attrname, old, new):
    """Update the Cv based on rhom input"""
    max_rhom = 0.5 * (slurry.rhos - slurry.rhol) + slurry.rhol
    slurry.rhom = check_value(rhom_input, 1.05, max_rhom, slurry.rhom, "0.3f")
    Cv_input.value=f"{slurry.Cv:0.3f}"
def Cv_up_callback():
    Cv_input.value=f"{slurry.Cv+0.005:0.3f}"
def Cv_down_callback():
    Cv_input.value=f"{slurry.Cv-0.005:0.3f}"
Cv_up_button = Button(label=u"\u25B2", width_policy="min", height_policy="min")
Cv_up_button.on_click(Cv_up_callback)
Cv_down_button = Button(label=u"\u25BC", width_policy="min", height_policy="min")
Cv_down_button.on_click(Cv_down_callback)
Cv_updown = column(Cv_up_button, Cv_down_button)
Cv_input = TextInput(title="Cv (-)", value=f"{slurry.Cv:0.3f}", width=95)
Cvi_input = TextInput(title=f'Cvi (\u03C1\u1D62 = {slurry.rhoi:0.3f})', value=f"{slurry.Cvi:0.3f}", disabled=True, width=95)
rhom_input = TextInput(title='Slurry Density \u03C1\u2098 (ton/m\u00b3)', value=f"{slurry.rhom:0.3f}", width=150)
rhom_input.on_change('value', update_rhom)
conc_row = row(rhom_input, Cv_input, Cv_updown, Spacer(width=10), Cvi_input)

def check_value(widget, min, max, prev, fmt):
    """Check and update or reset the value

    widget: The widget whose value to check
    min, max: minimum and maximum values of the input
    prev: The previous value (to reset of out of bounds)
    fmt: The format of the value in the widget (for resetting)

    Returns the final value of the widget after error check"""
    try:
        new = float(widget.value)
    except ValueError:
        print(f"{widget.title}: non numeric input")
        widget.value = f"{prev:{fmt}}"
        return prev
    if min <= new <= max:
        return new
    else:
        print(f"{widget.title}: value out of range")
        widget.value = f"{prev:{fmt}}"
        return prev

def update_data(attrname, old, new):
    # Get the current slider values

    d85 = check_value(D85_input,
                      slurry.D50*1000+0.01,
                      slurry.Dp * 1000 * 0.50,
                      slurry.get_dx(.85)*1000, '0.3f') / 1000
    slurry.D50 = check_value(D50_input,
                             max(slurry.get_dx(0.15)*1000+0.01,
                                 DHLLDV_framework.pseudo_dlim(slurry.Dp, slurry.nu, slurry.rhol, slurry.rhos)*1000),
                             min(slurry.get_dx(0.85)*1000-0.01,
                                 slurry.Dp * 1000 * 0.25),
                             slurry.D50 * 1000, '0.3f') / 1000
    d15 = check_value(D15_input, 0.08, slurry.D50 * 1000, slurry.get_dx(0.15)*1000, '0.3f') / 1000
    slurry.generate_GSD(d15_ratio=slurry.D50/d15, d85_ratio=d85/slurry.D50)
    slurry.Cv = check_value(Cv_input, 0.01, 0.5, slurry.Cv, '0.3f')
    update_source_data()

for w in [D15_input, D50_input, D85_input, Cv_input]:
    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = column(Div(text="""<B>Pipe</B>"""),
                Dp_row,             # A row of text boxes
                Spacer(background='lightblue', height=5, margin=(5,0,5,0)),
                Div(text="""<B>Fluid</B>"""),
                fluid_radio,
                fluid_properties,   # A row of text boxes
                Spacer(background='lightblue', height=5, margin=(5,0,5,0)),
                Div(text="""<B>Grain Size Distribution</B>"""),
                GSD_inputs,         # A row of text boxes
                GSD_plot,
                rhos_row,
                Spacer(background='lightblue', height=5, margin=(5,0,5,0)),
                Div(text="""<B>Concentrations</B>"""),
                conc_row,           # A row of text boxes
                )
plots = column(HQ_plot, Erhg_plot)
slurry_panel = Panel(child= row(inputs, plots), title="Slurry")

# Button to stop the server
def stop_button_callback():
    sys.exit()  # Stop the server
stop_button = Button(label="Stop", button_type="success", width=75)
stop_button.on_click(stop_button_callback)

sys_tab, sys_update = SystemTab.system_panel(pipeline)
curdoc().add_root(column(row(Spacer(width=1100), stop_button),
                         Tabs(tabs=[slurry_panel,
                                    sys_tab]),))
curdoc().title = "Visualizing DHLLDV"