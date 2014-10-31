'''
DHLLDV constants - contains some default values and constants for the DHLLDV model.
Created on Oct 8, 2014

@author: RCRamsdell
'''
from DHLLDV_Utils import interpDict

steel_roughness = 4.5e-05 #new steel pipe absolute roughness in m
gravity =  9.80665 #m/s2

water_density = interpDict({00:0.99984, #deg C, density in ton/m**3 per wikipedia
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
                            })

water_dynamic_viscosity = interpDict({00:1.7921E-03,   #Dynamic Viscosity (mu or eta) in Pa-s per wikipedia
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
                                      })

#Water kinematic viscosity in m2/sec
water_viscosity = interpDict(dict((t,water_dynamic_viscosity[t]/(1000*water_density[t])) for t in water_density.keys()))

Arel_to_beta = interpDict({0.00000:0.0000000,  #lookup table for calculating the angle beta for a given proportion of a pipe filled
                           0.00007:0.0698132,  #Arel = Adesired/Atotal
                           0.00058:0.1396263,  #beta in radians
                           0.00193:0.2094395,
                           0.00455:0.2792527,
                           0.01506:0.4188790,
                           0.03473:0.5585054,
                           0.10838:0.8377580,
                           0.16355:0.9773844,
                           0.23014:1.1170107,
                           0.25000:1.1549420,
                           0.28659:1.2217305,
                           0.33709:1.3089969,
                           0.39001:1.3962634,
                           0.44459:1.4835299,
                           0.50000:1.5707963,
                           0.55541:1.6580628,
                           0.60999:1.7453293,
                           0.66291:1.8325957,
                           0.71341:1.9198622,
                           0.76986:2.0245819,
                           0.83645:2.1642083,
                           0.89162:2.3038346,
                           0.96527:2.5830873,
                           0.98494:2.7227136,
                           0.99545:2.8623400,
                           0.99807:2.9321531,
                           0.99942:3.0019663,
                           0.99993:3.0717795,
                           1.00000:3.1415927,
                           })