'''
DHLLDV constants - contains some default values and constants for the DHLLDV model.
Created on Oct 8, 2014

@author: RCRamsdell
'''

water_density = {00:0.99984, #deg C, density in ton/m**3 per wikipedia
                 04:0.99997,
                 05:0.99996,
                 10:0.99970,
                 15:0.99910,
                 20:0.99820,
                 25:0.99704,
                 30:0.99564,
                 35:0.99403,
                 40:0.99221,
                 45:0.99022,
                 50:0.98804,
                 55:0.98570,
                 60:0.98321,
                 65:0.98056,
                 70:0.97778,
                 75:0.97486,
                 80:0.97180,
                 85:0.96862,
                 90:0.96531,
                 95:0.96189,
                 100:0.95835,
                 }

water_dynamic_viscosity = {00:1.7921E-03,   #Dynamic Viscosity (mu or eta) in Pa-s per wikipedia
                           04:1.5717E-03,
                            05:1.5188E-03,
                            10:1.3077E-03,
                            15:1.1404E-03,
                            20:1.0050E-03,
                            25:8.9370E-04,
                            30:8.0070E-04,
                            35:7.2250E-04,
                            40:6.5600E-04,
                            45:5.9880E-04,
                            50:5.4940E-04,
                            55:5.0640E-04,
                            60:4.6880E-04,
                            65:4.3550E-04,
                            70:4.0610E-04,
                            75:3.7990E-04,
                            80:3.6350E-04,
                            85:3.3550E-04,
                            90:3.1650E-04,
                            95:2.9940E-04,
                            100:2.8380E-04,
                            }

#Water kinematic viscosity in m2/sec
water_viscosity = dict((t,water_dynamic_viscosity[t]/(1000*water_density[t])) for t in water_density.keys())

steel_roughness = 4.5e-05 #new steel pipe absolute roughness in m
gravity =  9.80665 #m/s2