'''
bokeh_viewer: a program to view the curves in a bokeh interactive session

Added by R. Ramsdell 19 August, 2021
'''

''' Present an interactive function explorer with slider widgets.

Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve sliders.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/sliders
in your browser.
'''
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput
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
        self.Rsd = (self.rhos - self.rhol) / self.rhol
        self.Cv = 0.175
        self.rhom = self.Cv * self.Rsd
        self.vls_list = [(i + 1) / 10. for i in range(self.max_index)]
        self.generate_GSD()
        self.generate_curves()

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

im_source = ColumnDataSource(data=dict(x=slurry.vls_list, y=slurry.im_curves['graded_Cvt_im']))
uCvs_source = ColumnDataSource(data=dict(x=slurry.vls_list, y=slurry.im_curves['Cvs_im']))

# Set up plot
plot = figure(height=450, width=725, title="im curves",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 10], y_range=[0, 0.6])

plot.line('x', 'y', source=im_source,
          color='black',
          line_dash='dashed',
          line_width=3,
          line_alpha=0.6,
          legend_label='graded Sand Cvt=c')

plot.line('x', 'y', source=uCvs_source,
          color='red',
          line_dash='solid',
          line_width=3,
          line_alpha=0.6,
          legend_label='uniform Sand Cvs=c')

plot.legend.location = "top_left"

# Set up widgets
text = TextInput(title="title", value='my sine wave')
Dp_input = TextInput(title="Dp (mm)", value=f"{int(slurry.Dp*1000):0.0f}")
d_input = TextInput(title="d (mm)", value=f"{slurry.d*1000:0.3f}")
Cv_input = TextInput(title="Cv", value=f"{slurry.Cv:0.3f}")

# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value

text.on_change('value', update_title)

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

    im_source.data = dict(x=slurry.vls_list, y=slurry.im_curves['graded_Cvt_im'])
    uCvs_source.data = dict(x=slurry.vls_list, y=slurry.im_curves['Cvs_im'])

for w in [Dp_input, d_input, Cv_input]:
    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = column(text, Dp_input, d_input, Cv_input)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "im_Curves"