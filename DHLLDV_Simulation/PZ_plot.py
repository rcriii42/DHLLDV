"""Create a new pressure/elevation (hydraulic gradeline) plot"""
from bokeh.models import HoverTool, ColumnDataSource, Range1d, LinearAxis
from bokeh.plotting import figure

from DHLLDV.LagrPipe import LagrPipeline
from DHLLDV.PipeObj import Pipeline, Pipe
from unit_conv import unit_conv_SI, unit_label_SI, convert_list

unit_convs = unit_conv_SI
unit_labels = unit_label_SI


def create_hydraulic_gradeline(pipeline: Pipeline | LagrPipeline) -> (figure, ColumnDataSource):
    """Create a hydraulic gradeline plot"""
    hyd_hover = HoverTool(tooltips=[('name', "$name"),
                                    ('Section:', "@names"),
                                    (f"Location ({unit_labels['len']})", "@x{0.0}"),
                                    (f"Elevation ({unit_labels['len']})", "@e{0.0}"),
                                    (f"Pressure ({unit_labels['pressure']})", "@h{0.1}"),
                                    ])
    flow_list = [pipeline.pipesections[-1].flow(v) for v in pipeline.slurry.vls_list]
    qop = pipeline.find_operating_point(flow_list)
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

    return hyd_plot, hyd_source


def update_hydraulic_gradeline(hyd_plot: figure, hyd_source: ColumnDataSource, pipeline: Pipeline | LagrPipeline):
    """Update the given hydraulic gradeline plot"""
    flow_list = [pipeline.pipesections[-1].flow(v) for v in pipeline.slurry.vls_list]
    qop = pipeline.find_operating_point(flow_list)
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
    hyd_plot.y_range.end = max(h) * unit_convs['pressure'] * 1.01
    hyd_plot.yaxis[1].axis_label = f"Elevation ({unit_labels['len']})"
    hyd_plot.extra_y_ranges['e'].start = min(e) * unit_convs['len']
    hyd_plot.extra_y_ranges['e'].end = (max(e) + (max(e) - min(e)) * 2) * unit_convs['len']
    hyd_plot.tools[5].tooltips = [('name', "$name"),
                                  ('Section:', "@names"),
                                  (f"Location ({unit_labels['len']})", "@x{0.0}"),
                                  (f"Elevation ({unit_labels['len']})", "@e{0.0}"),
                                  (f"Pressure ({unit_labels['pressure']})", "@h{0.1}"),
                                  ]