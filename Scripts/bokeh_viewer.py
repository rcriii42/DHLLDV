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
max_index = 100
Dp = 0.1524  # Pipe diameter
d = 0.2 / 1000.
GSD = {0.15: d / 2.72,
       0.50: d,
       0.85: d * 2.72}
epsilon = DHLLDV_constants.steel_roughness
nu = 1.0508e-6  # DHLLDV_constants.water_viscosity[20]
rhos = 2.65
rhol = 1.0248103  # DHLLDV_constants.water_density[20]
Rsd = (rhos - rhol) / rhol
Cv = 0.175
rhom = Cv * (rhos - rhol) + rhol
vls_list = [(i + 1) / 10. for i in range(max_index)]
Erhg_curves = viewer.generate_Erhg_curves(vls_list, Dp, GSD[0.5], epsilon, nu, rhol, rhos, Cv, GSD)
im_curves = viewer.generate_im_curves(Erhg_curves, Rsd, Cv, rhom)
LDV_curves = viewer.generate_LDV_curves(Dp, GSD[0.5], epsilon, nu, rhol, rhos)

im_source = ColumnDataSource(data=dict(x=vls_list, y=im_curves['graded_Cvt_im']))

# Set up plot
plot = figure(height=400, width=400, title="im curves",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 10], y_range=[0, 0.6])

plot.line('x', 'y', source=im_source, line_width=3, line_alpha=0.6)

# Set up widgets
text = TextInput(title="title", value='my sine wave')
Dp_input = TextInput(title="Dp (mm)", value=f"{int(Dp*1000):0.0f}")
d_input = TextInput(title="d (mm)", value=f"{d*1000:0.3f}")
Cv_input = TextInput(title="Cv", value=f"{Cv:0.3f}")

# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value

text.on_change('value', update_title)

def check_value(min, max, prev):
    """Check and update or reset the value"""
    pass

def update_data(attrname, old, new):
    print(f"Update_Data: {attrname}, {old}, {new}")
    # Get the current slider values
    Dp = float(Dp_input.value)/1000
    d = float(d_input.value)/1000
    GSD = {0.15: d / 2.72,
           0.50: d,
           0.85: d * 2.72}
    Cv = float(Cv_input.value)

    # Generate the new curve
    Erhg_curves = viewer.generate_Erhg_curves(vls_list, Dp, GSD[0.5], epsilon, nu, rhol, rhos, Cv, GSD)
    im_curves = viewer.generate_im_curves(Erhg_curves, Rsd, Cv, rhom)
    LDV_curves = viewer.generate_LDV_curves(Dp, GSD[0.5], epsilon, nu, rhol, rhos)

    im_source.data = dict(x=vls_list, y=im_curves['graded_Cvt_im'])

for w in [Dp_input, d_input, Cv_input]:
    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = column(text, Dp_input, d_input, Cv_input)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "im_Curves"