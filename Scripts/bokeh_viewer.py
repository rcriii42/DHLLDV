'''
bokeh_viewer: a program to view the curves in a bokeh interactive session

Execute by running 'bokeh serve --show .\Scripts\bokeh_viewer.py' to open a tab in your browser

Added by R. Ramsdell 19 August, 2021
'''

import sys

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Button
from bokeh.plotting import figure

from DHLLDV import DHLLDV_constants
import viewer


# Set up data
class Slurry():
    def __init__(self):
        self.max_index = 100
        self.Dp = 0.1524  # Pipe diameter
        self.d = 0.2 / 1000.
        self.epsilon = DHLLDV_constants.steel_roughness
        self.nu = 1.0508e-6  # DHLLDV_constants.water_viscosity[20]
        self.rhos = 2.65
        self.rhol = 1.0248103  # DHLLDV_constants.water_density[20]
        self.rhoi = 1.92
        self.Cv = 0.175
        self.vls_list = [(i + 1) / 10. for i in range(self.max_index)]
        self.generate_GSD()
        self.generate_curves()

    @property
    def Rsd(self):
        return (self.rhos - self.rhol) / self.rhol

    @property
    def Cvi(self):
        return (self.rhom - self.rhol) / (self.rhoi - self.rhol)

    @property
    def rhom(self):
        return self.Cv * (self.rhos - self.rhol) + self.rhol

    def generate_GSD(self, d15_ratio=2.72, d85_ratio=2.72):
        self.GSD = {0.15: self.d / d15_ratio,
                    0.50: self.d,
                    0.85: self.d * d85_ratio}

    def generate_curves(self):
        self.Erhg_curves = viewer.generate_Erhg_curves(self.vls_list, self.Dp, self.GSD[0.5], self.epsilon,
                                                       self.nu, self.rhol, self.rhos, self.Cv, self.GSD)
        self.im_curves = viewer.generate_im_curves(self.Erhg_curves, self.Rsd, self.Cv, self.rhom)
        self.LDV_curves = viewer.generate_LDV_curves(self.Dp, self.GSD[0.5], self.epsilon,
                                                     self.nu, self.rhol, self.rhos)
slurry = Slurry()

im_source = ColumnDataSource(data=dict(v=slurry.vls_list,
                                       graded_Cvt_im=slurry.im_curves['graded_Cvt_im'],
                                       Cvs_im=slurry.im_curves['Cvs_im'],
                                       regime=slurry.Erhg_curves['Cvs_regime']))
LDV50_source = ColumnDataSource(data=dict(v=slurry.LDV_curves['vls'],
                                          im=slurry.LDV_curves['im'],
                                          il=slurry.LDV_curves['il'],
                                          Erhg=slurry.LDV_curves['Erhg'],
                                          regime=slurry.LDV_curves['regime']))
Erhg_source = ColumnDataSource(data=dict(il=slurry.Erhg_curves['il'],
                                         graded_Cvt=slurry.Erhg_curves['graded_Cvt_Erhg'],
                                         Cvs=slurry.Erhg_curves['Cvs_Erhg'],
                                         regime=slurry.Erhg_curves['Cvs_regime']))
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
                 x_range=[0, 10], y_range=[0, 0.6],
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
             line_width=3,
             line_alpha=0.6,
             legend_label='uniform Sand Cvs=c',
             name='uniform Sand Cvs=c')

HQ_plot.line('v', 'im', source=LDV50_source,
             color='magenta',
             line_dash='solid',
             line_width=3,
             line_alpha=0.6,
             legend_label='LDV D50',
             name='LDV D50')

HQ_plot.xaxis[0].axis_label = 'Velocity (m/sec)'
HQ_plot.yaxis[0].axis_label = 'Head (m/m)'
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
                 x_range=[0.001, 1.0], y_range=[0.001, 1.2],
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
             line_width=3,
             line_alpha=0.6,
             legend_label='uniform Sand Cvs=c',
             name='uniform Sand Cvs=c')

Erhg_plot.line('il', 'Erhg', source=LDV50_source,
             color='magenta',
             line_dash='solid',
             line_width=3,
             line_alpha=0.6,
             legend_label='LDV D50',
             name='LDV D50')

Erhg_plot.xaxis[0].axis_label = 'Hydraulic Gradient il (m/m)'
Erhg_plot.yaxis[0].axis_label = 'Relative Excess Hydraulic Gradient Erhg (-)'
Erhg_plot.legend.location = "top_left"



# Set up widgets
Dp_input = TextInput(title="Dp (mm)", value=f"{int(slurry.Dp*1000):0.0f}")
d_input = TextInput(title="d (mm)", value=f"{slurry.d*1000:0.3f}")
Cv_input = TextInput(title="Cv", value=f"{slurry.Cv:0.3f}")
Cvi_input = TextInput(title='Cvi (@1.92)', value=f"{slurry.Cvi:0.3f}")
rhom_input = TextInput(title='Rhom', value=f"{slurry.rhom:0.3f}")


# Button to stop the server
def button_callback():
    sys.exit()  # Stop the server
button = Button(label="Stop", button_type="success")
button.on_click(button_callback)


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
    slurry.d = check_value(d_input, 0.08, slurry.Dp*1000*0.25, slurry.d*1000, '0.3f')/1000
    slurry.generate_GSD()
    slurry.Cv = check_value(Cv_input, 0.01, 0.5, slurry.Cv, '0.3f')

    # Generate the new curve
    slurry.generate_curves()

    im_source.data = data=dict(v=slurry.vls_list,
                               graded_Cvt_im=slurry.im_curves['graded_Cvt_im'],
                               Cvs_im=slurry.im_curves['Cvs_im'],
                               regime=slurry.Erhg_curves['Cvs_regime'])
    LDV50_source.data = dict(v=slurry.LDV_curves['vls'],
                             im=slurry.LDV_curves['im'],
                             il=slurry.LDV_curves['il'],
                             Erhg=slurry.LDV_curves['Erhg'],
                             regime=slurry.LDV_curves['regime'])
    Erhg_source.data = dict(il=slurry.Erhg_curves['il'],
                            graded_Cvt=slurry.Erhg_curves['graded_Cvt_Erhg'],
                            Cvs=slurry.Erhg_curves['Cvs_Erhg'],
                            regime=slurry.Erhg_curves['Cvs_regime'])
    Cvi_input.value = f"{slurry.Cvi:0.3f}"
    rhom_input.value = f"{slurry.rhom:0.3f}"


for w in [Dp_input, d_input, Cv_input]:
    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = column(Dp_input, d_input, Cv_input, Cvi_input, rhom_input, button)
plots = column(HQ_plot, Erhg_plot)

curdoc().add_root(row(inputs, plots, width=800))
curdoc().title = "im_Curves"