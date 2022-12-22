"""unit_conv - library for the unit conversion methods

Created by Robert.Ramsdell@DredgingResources.net 9/13/2022"""


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


def convert_list(conversion, values):
    """Covert the values in a list using the given conversion"""
    return [v*conversion for v in values]
