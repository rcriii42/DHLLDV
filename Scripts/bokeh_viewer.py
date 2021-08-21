'''
bokeh_viewer: a program to view the curves in a bokeh interactive session

Execute by running 'bokeh serve --show .\Scripts\bokeh_viewer.py' to open a tab in your browser

Added by R. Ramsdell 19 August, 2021
'''

import sys
from math import log10

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Button, RadioButtonGroup, Spacer
from bokeh.plotting import figure

from DHLLDV import DHLLDV_constants
from DHLLDV.DHLLDV_framework import pseudo_dlim
import viewer


# Set up data
class Slurry():
    def __init__(self):
        self.max_index = 100
        self.Dp = 0.762  # Pipe diameter
        self.D50 = 1.0 / 1000.
        self._silt = 0
        self.epsilon = DHLLDV_constants.steel_roughness
        self._fluid = 'salt'
        self.nu = 1.0508e-6  # DHLLDV_constants.water_viscosity[20]
        self.rhol = 1.0248103  # DHLLDV_constants.water_density[20]
        self.rhos = 2.65
        self.rhoi = 1.92
        self.Cv = 0.175
        self.vls_list = [(i + 1) / 10. for i in range(self.max_index)]
        self.generate_GSD()
        self.generate_curves()

    @property
    def fluid(self):
        return self._fluid

    @fluid.setter
    def fluid(self, fluid):
        if fluid == 'salt':
            self.nu = 1.0508e-6
            self.rhol = 1.0248103
        else:
            self.nu = DHLLDV_constants.water_viscosity[20]
            self.rhol = DHLLDV_constants.water_density[20]

    @property
    def silt(self):
        return self._silt

    @silt.setter
    def silt(self, X):
        if X < 0:
            X = 0.0
        if X > 1:   #In this case D85 is < 0.075 and the ELM will be invoked
            X = 0.999
        self._silt = X
        self.generate_GSD(d15_ratio=None, d85_ratio=None)

    @property
    def Rsd(self):
        return (self.rhos - self.rhol) / self.rhol

    @property
    def Cvi(self):
        return (self.rhom - self.rhol) / (self.rhoi - self.rhol)

    @property
    def rhom(self):
        return self.Cv * (self.rhos - self.rhol) + self.rhol

    def generate_GSD(self, d15_ratio=2.0, d85_ratio=2.72):
        if not d15_ratio:
            d15_ratio = self.GSD[0.5] / self.GSD[0.15]
        if not d85_ratio:
            d85_ratio = self.GSD[0.85] / self.GSD[0.5]
        self.GSD = {0.15: self.D50 / d15_ratio,
                    0.50: self.D50,
                    0.85: self.D50 * d85_ratio,
                    self._silt: 0.075/1000}
        # The limiting diameter for pseudoliquid and it's fraction X
        dmin = pseudo_dlim(self.Dp, self.nu, self.rhol, self.rhos)
        fracs = iter(sorted(self.GSD, key=lambda key: self.GSD[key]))
        flow = next(fracs)
        dlow = self.GSD[flow]
        fnext = next(fracs)
        dnext = self.GSD[fnext]
        while dmin > dnext:
            ftemp = next(fracs, None)
            if ftemp:
                dlow = dnext
                flow = fnext
                fnext = ftemp
                dnext = self.GSD[fnext]
            else:
                break
        X = fnext - (log10(dnext) - log10(dmin)) * (fnext - flow) / (log10(dnext) - log10(dlow))
        self.GSD[X] = dmin

    def generate_curves(self):
        self.Erhg_curves = viewer.generate_Erhg_curves(self.vls_list, self.Dp, self.GSD[0.5], self.epsilon,
                                                       self.nu, self.rhol, self.rhos, self.Cv, self.GSD)
        self.im_curves = viewer.generate_im_curves(self.Erhg_curves, self.Rsd, self.Cv, self.rhom)
        self.LDV_curves = viewer.generate_LDV_curves(self.Dp, self.GSD[0.5], self.epsilon,
                                                     self.nu, self.rhol, self.rhos)
        self.LDV85_curves = viewer.generate_LDV_curves(self.Dp, self.GSD[0.85], self.epsilon,
                                                       self.nu, self.rhol, self.rhos)
slurry = Slurry()

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
    viscosity_label.value=f"{slurry.nu:0.4e}"
    density_label.value=f"{slurry.rhol:0.4f}"
    Cvi_input.value = f"{slurry.Cvi:0.3f}"
    rhom_input.value = f"{slurry.rhom:0.3f}"
    percents = sorted(list(slurry.GSD.keys()))
    GSD_source.data = dict(p=percents, dia=[slurry.GSD[pct] * 1000 for pct in percents])

################
# Set up HQ plot
HQ_TOOLTIPS = [
    ('name', "$name"),
    ("vls (m/sec)", "$x"),
    ("H (m/m)", "$y"),
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

HQ_plot.line('v', 'Cvs_im', source=im_source,
             color='red',
             line_dash='solid',
             line_width=2,
             line_alpha=0.6,
             legend_label='uniform Sand Cvs=c',
             name='uniform Sand Cvs=c')

HQ_plot.line('v', 'Cvt_im', source=im_source,
             color='green',
             line_dash='dashed',
             line_width=2,
             line_alpha=0.6,
             legend_label='uniform Sand Cvt=c',
             name='uniform Sand Cvt=c')

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

HQ_plot.xaxis[0].axis_label = 'Velocity (m/sec)'
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

Erhg_plot.line('il', 'Cvs', source=Erhg_source,
             color='red',
             line_dash='solid',
             line_width=2,
             line_alpha=0.6,
             legend_label='uniform Sand Cvs=c',
             name='uniform Sand Cvs=c')

Erhg_plot.line('il', 'Cvt', source=Erhg_source,
             color='green',
             line_dash='dashed',
             line_width=2,
             line_alpha=0.6,
             legend_label='uniform Sand Cvt=c',
             name='uniform Sand Cvt=c')

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
GSD_plot.axis.major_tick_in = 10
GSD_plot.axis.minor_tick_in = 7
GSD_plot.axis.minor_tick_out = 0
GSD_plot.xgrid.minor_grid_line_color='navy'
GSD_plot.xgrid.minor_grid_line_alpha=0.1

# Set up widgets
def update_fluid(index):
    if index == 0:
        slurry.fluid = 'fresh'
    else:
        slurry.fluid = 'salt'
    update_source_data()

fluid_radio = RadioButtonGroup(labels=['Fresh', 'Salt'], active=1)
fluid_radio.on_click(update_fluid)
viscosity_label = TextInput(title=f"Viscosity (m\u00b2/sec)", value=f"{slurry.nu:0.4e}", width=100)
density_label = TextInput(title=f"Density (ton/m\u00b3)", value=f"{slurry.rhol:0.4f}", width=100)
fluid_properties = row(viscosity_label, density_label)

# Button to stop the server
def button_callback():
    sys.exit()  # Stop the server
button = Button(label="Stop", button_type="success")
button.on_click(button_callback)

def D50_adjust_proportionate(delta):
    new_D50 = slurry.D50 + delta / 1000
    new_D85 = new_D50 * slurry.GSD[0.85] / slurry.GSD[0.5]
    new_D15 = new_D50 * slurry.GSD[0.15] / slurry.GSD[0.5]
    D50_input.value = f"{new_D50 * 1000:0.3f}"
    D85_input.value = f"{new_D85 * 1000:0.3f}"
    D15_input.value = f"{new_D15 * 1000:0.3f}"
def D50_up_callback():
    D50_adjust_proportionate(0.1)
def D50_down_callback():
    D50_adjust_proportionate(-0.1)

D85_input = TextInput(title="D85 (mm)", value=f"{slurry.GSD[0.85] * 1000:0.3f}", width=95)
D50_input = TextInput(title="D50 (mm)", value=f"{slurry.D50 * 1000:0.3f}", width=95)
D50_up_button = Button(label=u"\u25B2", width_policy="min", height_policy="min") # , margin=(-5, -5, -5, -5))
D50_up_button.on_click(D50_up_callback)
D50_down_button = Button(label=u"\u25BC", width_policy="min", height_policy="min")
D50_down_button.on_click(D50_down_callback)
D15_input = TextInput(title="D15 (mm)", value=f"{slurry.GSD[0.15] * 1000:0.3f}", width=95)
silt_input = TextInput(title="Silt (% of 0.075 mm)", value=f"{slurry.silt * 100:0.1f}", width=95)
Dp_input = TextInput(title="Dp (mm)", value=f"{int(slurry.Dp*1000):0.0f}")
Cv_input = TextInput(title="Cv", value=f"{slurry.Cv:0.3f}")
Cvi_input = TextInput(title='Cvi (@1.92)', value=f"{slurry.Cvi:0.3f}")
rhom_input = TextInput(title='Rhom', value=f"{slurry.rhom:0.3f}")

def check_value(widget, min, max, prev, fmt):
    """Check and update or reset the value

    widget: The widget whose value to check
    min, max: minimum and maximum values of the input
    prev: The previous value (to reset of out of bounds)
    fmt: The format of the value in the widget (for resetting)"""
    print(f"{widget.title}: New: {widget.value}, Bounds:{min} - {max}, Was:{prev:{fmt}}")
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
    print(f"Update_Data: {attrname}, {old}, {new}")
    # Get the current slider values
    slurry.Dp = check_value(Dp_input, 25, 1500, slurry.Dp*1000, '0.0f')/1000
    slurry.GSD[0.85] = check_value(D85_input, slurry.D50*1000, slurry.Dp * 1000 * 0.50, slurry.GSD[0.85]*1000, '0.3f') / 1000
    slurry.D50 = check_value(D50_input, 0.08, slurry.Dp * 1000 * 0.25, slurry.D50 * 1000, '0.3f') / 1000
    slurry.GSD[0.15] = check_value(D15_input, 0.06, slurry.D50 * 1000, slurry.GSD[0.15]*1000, '0.3f') / 1000
    slurry.silt = check_value(silt_input, 0.0, 49.99, slurry.silt, '0.1f')/100
    slurry.generate_GSD(d15_ratio=None, d85_ratio=None)
    slurry.Cv = check_value(Cv_input, 0.01, 0.5, slurry.Cv, '0.3f')

    update_source_data()


for w in [Dp_input, D15_input, D50_input, D85_input, silt_input, Cv_input]:
    w.on_change('value', update_data)

# Set up layouts and add to document
updown = column(D50_up_button, D50_down_button)
GSD_inputs = row(D85_input, D50_input, updown, D15_input, silt_input)
inputs = column(fluid_radio,
                fluid_properties,           # A row of text boxes
                Spacer(background='lightblue', height=5),
                GSD_inputs,                 # A row of text boxes
                GSD_plot,
                Spacer(background='lightblue', height=5),
                Dp_input,
                Cv_input,
                Cvi_input,
                rhom_input,
                button)
plots = column(HQ_plot, Erhg_plot)

curdoc().add_root(row(inputs, plots, width=800))
curdoc().title = "im_Curves"