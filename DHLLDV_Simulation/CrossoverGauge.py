"""Class to simulate a dredging crossover gauge in Bokeh"""
from math import asin, pi, cos, sin, tan

from bokeh.models import ColumnDataSource, Label
from bokeh.plotting import figure


class CrossoverGauge:
    """A class to simulate a crossover velocity/density gauge with a middle axis indicating production"""
    def __init__(self,
                 vel_max_angle=45, vel_max_value=5.5, vel_pointer_origin=(1, 0),
                 den_max_angle=45, den_max_value=1.3, den_pointer_origin=(-1, 0),
                 rhof=1.025, rhos=2.65, rhoi=1.95, pipe_dia=(10/12)*0.3048) -> None:
        self.vel_max_angle = vel_max_angle
        self.vel_min_value = 0.0
        self.vel_max_value = vel_max_value
        self.vel_pointer_origin = vel_pointer_origin
        self.den_max_angle = den_max_angle
        self.den_min_value = 1.0
        self.den_max_value = den_max_value
        self.den_pointer_origin = den_pointer_origin

        self.rhof = rhof
        self.rhos = rhos
        self.rhoi = rhoi
        self.Dp = pipe_dia

        self.tick_len = 1.05  # Length of the tick relative to the axis radius

        self.figure = figure(height=375,
                             x_range=(den_pointer_origin[0]*1.5, vel_pointer_origin[0]*1.5),
                             y_range=(-0.1, 0.85 * (self.vel_pointer_origin[0] - self.den_pointer_origin[0])),
                             tools="", outline_line_color="black")
        self.figure.xaxis.visible = False
        self.figure.yaxis.visible = False
        self.draw_side_axis('vel')
        self.draw_side_axis('den')
        self.middle_axis_labels = []
        self.draw_middle_axis()

        self.pointer_data = ColumnDataSource(data=dict(vel_x=[vel_pointer_origin[0], den_pointer_origin[0]],
                                                       vel_y=[vel_pointer_origin[1], den_pointer_origin[1]],
                                                       den_x=[den_pointer_origin[0], vel_pointer_origin[0]],
                                                       den_y=[den_pointer_origin[1], vel_pointer_origin[1]]))
        self.figure.line(source=self.pointer_data, x='vel_x', y='vel_y', color="red")
        self.figure.line(source=self.pointer_data, x='den_x', y='den_y', color="red")
        self.update(vel_max_value/2, 1+(den_max_value-1)/2)

    @property
    def Ap(self):
        """Return the area of the pipe in m2"""
        return pi * (self.Dp / 2)**2

    def update(self, vel, den,
               rhof=None, rhos=None, rhoi=None, pipe_dia=None):
        """Update the crossover gauge"""
        pointer_radius = (self.vel_pointer_origin[0] - self.den_pointer_origin[0]) * 1 + (self.tick_len - 1) / 2
        vel_angle = pi - (vel * self.vel_max_angle / self.vel_max_value) * pi / 180
        den_angle = ((den - 1) * self.den_max_angle / (self.den_max_value - 1)) * pi / 180
        self.pointer_data.data = dict(vel_x=[self.vel_pointer_origin[0],
                                             self.vel_pointer_origin[0] + pointer_radius * cos(vel_angle)],
                                      vel_y=[self.vel_pointer_origin[1],
                                             self.vel_pointer_origin[1] + pointer_radius * sin(vel_angle)],
                                      den_x=[self.den_pointer_origin[0],
                                             self.den_pointer_origin[0] + pointer_radius * cos(den_angle)],
                                      den_y=[self.den_pointer_origin[1],
                                             self.den_pointer_origin[1] + pointer_radius * sin(den_angle)])

        if any([rhof, rhos, rhoi, pipe_dia]):  # Update the middle axis scale
            self.rhof = rhof
            self.rhos = rhos
            self.rhoi = rhoi
            self.Dp = pipe_dia
            for i in range(1, 6):
                x_center = 0
                y_center = i * 0.2
                angle_center = asin((y_center - self.vel_pointer_origin[1]) /
                                    ((x_center - self.vel_pointer_origin[0]) ** 2 +
                                     (y_center - self.vel_pointer_origin[1]) ** 2) ** 0.5)
                vel_center = angle_center * self.vel_max_value / (self.vel_max_angle * pi / 180)
                den_center = angle_center * (self.den_max_value - 1) / (self.den_max_angle * pi / 180) + 1
                prod_center = vel_center * self.Ap * ((den_center - self.rhof) / (self.rhoi - self.rhof))
                self.middle_axis_labels[i-1].text = f'{prod_center*3600:0.0f}'

    def draw_middle_axis(self):
        """Calculate and draw the middle axis"""
        for i in range(1, 6):
            x_center = 0
            y_center = i * 0.2
            angle_center = asin((y_center - self.vel_pointer_origin[1]) /
                                ((x_center - self.vel_pointer_origin[0])**2 +
                                 (y_center - self.vel_pointer_origin[1])**2)**0.5)
            vel_center = angle_center * self.vel_max_value / (self.vel_max_angle * pi / 180)
            den_center = angle_center * (self.den_max_value - 1) / (self.den_max_angle * pi / 180) + 1
            prod_center = vel_center * self.Ap * ((den_center - self.rhof)/(self.rhoi - self.rhof))
            lbl = Label(x=x_center - 0.08, y=y_center + 0.02, text=f'{prod_center*3600:0.0f}')
            self.figure.add_layout(lbl)
            self.middle_axis_labels.append(lbl)

            # Now draw points of equal production starting at the maximum density
            x_list = [x_center]
            y_list = [y_center]
            den_min_angle = ((self.rhof - 1) * self.den_max_angle / (self.den_max_value - 1)) * pi / 180
            alpha_d = self.den_max_angle * 1.01 * pi / 180
            delta_alpha = (alpha_d - den_min_angle) / 10
            i = 11
            while True:
                # Lower density and calculate the velocity that maintains production
                if i <= 0:
                    break
                rhom = 1 + (self.den_max_value - 1) * alpha_d / (self.den_max_angle * pi / 180)
                if rhom <= self.rhof:
                    # One more point at maximum velocity
                    vm = self.vel_max_value * 1.01
                    rhom = prod_center * (self.rhoi - self.rhof)/(vm * self.Ap) + self.rhof
                    alpha_d = (rhom - 1) * (self.den_max_angle * pi / 180) / (self.den_max_value - 1)

                    i = 0   # End the loop after this point
                i -= 1
                Cvi = (rhom - self.rhof) / (self.rhoi - self.rhof)
                vm = prod_center / (Cvi * self.Ap)
                if vm > self.vel_max_value:
                    # One more point at maximum velocity
                    vm = self.vel_max_value * 1.01
                    rhom = prod_center * (self.rhoi - self.rhof) / (vm * self.Ap) + self.rhof
                    alpha_d = (rhom - 1) * (self.den_max_angle * pi / 180) / (self.den_max_value - 1)
                    i = 0

                # The angles of the velocity and density pointers
                alpha_v = pi - vm * (self.vel_max_angle * pi / 180) / self.vel_max_value
                # alpha_d = (rhom - self.rhof) * self.den_max_angle * pi / 180 / (self.den_max_value - self.rhof)

                # The x,y position
                xc = (self.den_pointer_origin[0] * tan(alpha_d) - self.vel_pointer_origin[0] * tan(alpha_v) +
                      self.vel_pointer_origin[1] - self.den_pointer_origin[1]) / (tan(alpha_d) - tan(alpha_v))
                yc = ((xc - self.vel_pointer_origin[0]) * tan(alpha_v) + self.vel_pointer_origin[1])
                if rhom > den_center:
                    x_list.insert(-1, xc)
                    y_list.insert(-1, yc)
                elif rhom < den_center:
                    x_list.append(xc)
                    y_list.append(yc)
                else:
                    pass
                alpha_d -= delta_alpha

            self.figure.line(x=x_list, y=y_list, color="blue")

    def draw_side_axis(self, side='vel'):
        """Draw the velocity axis on the left"""
        side_axis_radius = self.vel_pointer_origin[0] - self.den_pointer_origin[0]
        if side == 'vel':
            side_origin_x = self.vel_pointer_origin[0]
            side_origin_y = self.vel_pointer_origin[1]
            side_start_angle = pi
            side_end_angle = pi - self.vel_max_angle * pi / 180
            side_min_tick = self.vel_min_value
            side_tick_gap = 0.5
            side_num_ticks = int((self.vel_max_value - self.vel_min_value) / side_tick_gap) + 1
            if side_num_ticks > 10:
                side_tick_gap = 1.0
                side_num_ticks = int((self.vel_max_value - self.vel_min_value) / side_tick_gap) + 1
            side_tick_anchor = 'center_right'

            def delta_tick(tick_val):
                """Determine the tick angle offset from horiz based on the value"""
                return (-1 * tick_val * self.vel_max_angle / self.vel_max_value) * pi / 180
        else:
            side_origin_x = self.den_pointer_origin[0]
            side_origin_y = self.den_pointer_origin[1]
            side_start_angle = 0
            side_end_angle = self.den_max_angle * pi / 180
            side_min_tick = self.den_min_value
            side_tick_gap = .05
            side_num_ticks = int((self.den_max_value - self.den_min_value) / side_tick_gap) + 1
            side_tick_anchor = 'center_left'

            def delta_tick(tick_val):
                """Determine the tick angle offset from horiz based on the value"""
                return (tick_val - 1) * self.den_max_angle / (self.den_max_value - 1) * pi / 180
        # The axis line is an arc centered on the pointer origin and touching the other.
        num_segments = 50
        segment_angle = (side_end_angle - side_start_angle)/num_segments
        axis_angles = [side_start_angle + a * segment_angle for a in range(num_segments + 1)]
        axis_x = [side_origin_x + side_axis_radius*cos(a) for a in axis_angles]
        axis_y = [side_origin_y + side_axis_radius*sin(a) for a in axis_angles]
        self.figure.line(x=axis_x, y=axis_y)

        # The axis tick marks
        for i in range(side_num_ticks):
            tick_value = side_min_tick + i * side_tick_gap
            tick_angle = side_start_angle + delta_tick(tick_value)
            x_ticks = [side_origin_x + side_axis_radius*cos(tick_angle),
                       side_origin_x + self.tick_len*side_axis_radius*cos(tick_angle)]
            y_ticks = [side_origin_y + side_axis_radius*sin(tick_angle),
                       side_origin_y + self.tick_len*side_axis_radius*sin(tick_angle)]
            self.figure.line(x=x_ticks,
                             y=y_ticks)
            if side_tick_anchor == "center_right":
                x_offset = -0.2
            else:
                x_offset = 0.0
            self.figure.add_layout(Label(x=x_ticks[1]+x_offset, y=y_ticks[1], text=f'{tick_value:0.2f}'))
