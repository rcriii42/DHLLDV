'''
Created on Mar 3, 2015

@author: rcriii
'''

import stratified, heterogeneous, homogeneous


def Cvs_Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, get_dict=False):
    """
    Cvs_Erhg - Calculate the Erhg for the given slurry, using the appropriate model
    vls = average line speed (velocity, m/sec)
    Dp = Pipe diameter (m)
    d = Particle diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cvs = insitu volume concentration
    get_dict: if true return the dict with all models.
    """
    Erhg_obj={'FB':stratified.fb_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
              'SB':   stratified.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
              'He':heterogeneous.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
              'Ho':  homogeneous.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
              }
    
    
    if Erhg_obj['FB'] < Erhg_obj['SB']:
        regime = 'FB'
    else:
        regime = 'SB'
    
    if Erhg_obj[regime] > Erhg_obj['He']:
        regime = 'He'
    
    if Erhg_obj[regime] < Erhg_obj['Ho']:
        regime = 'Ho'
    
    Erhg_obj['regime'] = regime
    
    if get_dict:
        return Erhg_obj
    else:
        return Erhg_obj[Erhg_obj['regime']]


def Cvs_regime(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs):
    """
    Cvs_regime - Rteurn the name of the regime for the given model
    vls = average line speed (velocity, m/sec)
    Dp = Pipe diameter (m)
    d = Particle diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cvs = insitu volume concentration
    """
    Erhg_obj = Cvs_Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, get_dict=True)
    return {'FB': 'fixed bed',
            'SB': 'sliding bed',
            'He': 'heterogeneous',
            'Ho': 'homogeneous',
            }[Erhg_obj['regime']]


if __name__ == '__main__':
    pass
