"""
Created on Mar 3, 2015

@author: rcriii
"""

from . import stratified
from . import heterogeneous
from . import homogeneous
from .DHLLDV_constants import gravity, particle_ratio, stk_fine
from math import pi, exp, log10

alpha_xi = 0.5    # alpha in Eqn 8.12-9

use_sf = True        # use these corrections by default, but can be overridden
use_sqrtcx = True


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
    Erhg_obj = {'il': homogeneous.fluid_head_loss(vls, Dp, epsilon, nu, rhol),
                'FB': stratified.fb_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
                'SB':    stratified.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
                'He': heterogeneous.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, use_sf, use_sqrtcx),
                'Ho':   homogeneous.Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs),
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
    Return the name of the regime for the given slurry and velocity
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


def LDV(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvs, max_steps=10):
    """
    Return the LDV for the given slurry.
    vls: not used, included for consistency sake
    Dp = Pipe diameter (m)
    d = Particle diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cvs = insitu volume concentration
    """
    Rsd = (rhos-rhol)/rhol
    fbot = (2*gravity*Rsd*Dp)**0.5

    # Very Small Particles
    vls = 1.0
    Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
    lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
    FL_vs = 1.4*(nu*Rsd*gravity)**(1./3.)*(8/lambdal)**0.5/fbot  # Eqn 8.11-1
    vlsldv = FL_vs*fbot
    steps = 0
    while not (1.00001 >= vls/vlsldv > 0.99999) and steps < max_steps:
        vls = (vls + vlsldv)/2
        Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
        lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
        FL_vs = 1.4*(nu*Rsd*gravity)**(1./3.)*(8/lambdal)**0.5/fbot  # Eqn 8.11-1
        vlsldv = FL_vs*fbot
        steps += 1

    # Small Particles
    vls = 4.0
    Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
    lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
    alphap = 3.4 * (1.65/Rsd)**(2./9)  # Eqn 8.11-3
    vt = heterogeneous.vt_ruby(d, Rsd, nu)
    Rep = vt*d/nu  # Eqn 4.2-6
    top = 4.7 + 0.41*Rep**0.75
    bottom = 1. + 0.175*Rep**0.75
    beta = top/bottom  # Eqn 4.6-4
    KC = 0.175*(1+beta)
    FL_ss = alphap * (vt*Cvs*(1-Cvs/KC)**beta/(lambdal*fbot))**(1./3)  # Eqn 8.11-3
    vlsldv = FL_ss*fbot
    steps = 0
    while not (1.00001 >= vls/vlsldv > 0.99999) and steps < max_steps:
        vls = (vls + vlsldv)/2
        Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
        lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
        FL_ss = alphap * (vt*Cvs*(1-Cvs/KC)**beta/(lambdal*fbot))**(1./3)  # Eqn 8.11-3
        vlsldv = FL_ss*fbot
        steps += 1

    FL_s = max(FL_vs, FL_ss)    # Eqn 8.11-4

    # Large particles
    vls = 4.3
    if d <= 0.015*Dp:
        Cvr_ldv = 0.0065/(2*gravity*Rsd*Dp)  # Eqn 8.11-7
    else:
        Cvr_ldv = 0.053*(d/Dp)**0.5/(2*gravity*Rsd*Dp)  # Eqn 8.11-7
    Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
    lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
    FL_r = alphap*((1-Cvs/KC)**beta * Cvs *
                   (stratified.musf*stratified.Cvb*pi/8)**0.5 * Cvr_ldv**0.5/lambdal)**(1./3)  # Eqn 8.11-6
    vlsldv = FL_r*fbot
    steps = 0
    while not (1.00001 >= vls/vlsldv > 0.99999) and steps < max_steps:
        vls = (vls + vlsldv)/2
        Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
        lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
        FL_r = alphap*((1-Cvs/KC)**beta * Cvs *
                       (stratified.musf*stratified.Cvb*pi/8)**0.5 * Cvr_ldv**0.5/lambdal)**(1./3)  # Eqn 8.11-6
        vlsldv = FL_r*fbot
        steps += 1

    # The Upper limit
    d0 = 0.0005*(1.65/Rsd)**0.5  # Eqn 8.11-8
    drough = 2./1000  # Note: only valid for sand with Rsd=1.65
    if d > drough:
        FL_ul = FL_r
    elif FL_s <= FL_r:
        FL_ul = FL_s
    else:
        FL_ul = FL_s*exp(-1*d/d0) + FL_r*(1-exp(-1*d/d0))   # Eqn 8.11-8

    vls = 2.0
    Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
    lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
    A = -1
    B = vt*(1-Cvs/KC)**beta/stratified.musf
    C = ((8.5**2/lambdal)*(vt/(gravity*d)**0.5)**(10./3)*(nu*gravity)**(2./3))/stratified.musf
    vlsldv = (-1*B - (B**2-4*A*C)**0.5)/(2*A)   # Eqn 8.10-11
    steps = 0
    while not (1.00001 >= vls/vlsldv > 0.99999) and steps < max_steps:
        vls = (vls + vlsldv)/2
        Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
        lambdal = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
        A = -1
        B = vt*(1-Cvs/KC)**beta/stratified.musf
        C = ((8.5**2/lambdal)*(vt/(gravity*d)**0.5)**(10./3)*(nu*gravity)**(2./3))/stratified.musf
        vlsldv = (-1*B - (B**2-4*A*C)**0.5)/(2*A)   # Eqn 8.11-11
        steps += 1
    FL_ll = vlsldv/fbot  # Eqn 8.11-12

    FL = max(FL_ul, FL_ll)  # Eqn 8.11-13
    return FL*fbot


def slip_ratio(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvt):
    """
    Return the slip ratio (Xi) for the given slurry.
    Dp = Pipe diameter (m)
    d = Particle diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cvt = transport volume concentration
    """
    if vls == 0.0:
        vls = 0.01
    Rsd = (rhos - rhol)/rhol     # Eqn 8.2-1
    Cvb = stratified.Cvb
    Cvr = Cvt/Cvb
    vt = heterogeneous.vt_ruby(d, Rsd, nu)  # Particle shape factor assumed for sand for now
    CD = (4/3.)*((gravity*Rsd*d)/vt**2)     # Eqn 4.4-6 without the shape factor
    Rep = vt*d/nu       # Eqn 4.2-6
    top = 4.7 + 0.41*Rep**0.75
    bottom = 1. + 0.175*Rep**0.75
    beta = top/bottom   # Eqn 4.6-4
    KC = 0.175*(1+beta)
    vls_ldv = LDV(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt)
    vls_lsdv = stratified.vls_lsdv(Dp,  d, epsilon, nu, rhol, rhos, Cvt)

    Re = homogeneous.pipe_reynolds_number(vls, Dp, nu)
    lambda_l = homogeneous.swamee_jain_ff(Re, Dp, epsilon)
    Xi_HeHo = 8.5*(1/lambda_l)*(vt/(gravity*d)**0.5)**5/3*((nu*gravity)**(1/3)/vls)*(vt/vls)  # Eqn 8.12-1

    alpha = 0.58*Cvr**-0.42
    ex1 = -(0.83 + stratified.musf/4 + (Cvr - 0.5 - 0.075*Dp)**2 + (0.025*Dp))
    ex2 = Dp**0.025*(vls_ldv/vls_lsdv)**alpha*Cvr**0.65*(Rsd/1.585)**0.1
    Xi_ldv = (1-Cvr) * exp(ex1*ex2)  # Eqn 8.12-2
    Xi_aldv = Xi_ldv * (vls_ldv/vls)**4
    vls_t = (5 * exp(ex1 * ex2)) ** 0.25 * vls_ldv  # Eqn 8.12-7

    Kldv = 1/(1 - Xi_ldv)       # Eqn 7.9-14
    Xi_fb = 1-((Cvt*vls_ldv)/(Cvb-Kldv*Cvt)*(vls_ldv-vls)+Kldv*Cvt*vls_ldv)  # Eqn 8.12-3

    ex2 = Dp ** 0.025 * (vls / vls_lsdv) ** alpha * Cvr ** 0.65 * (Rsd / 1.585) ** 0.1
    Xi_3LM = (1 - Cvr) * exp(ex1 * ex2)  # Eqn 8.12-4

    if Xi_fb < Xi_aldv:     # Eqn 8.12-5
        Xi_th = Xi_fb
    elif Xi_HeHo > Xi_aldv:
        Xi_th = Xi_HeHo
    else:
        Xi_th = Xi_aldv

    if vls < vls_t:
        Xi_t = (1 - Cvr) * (1 - (4. / 5.) * (vls / vls_t))  # Eqn 8.12-8
        Xi_SBHeHo = Xi_th*(1-(vls/vls_t)**alpha_xi) + Xi_t*(vls/vls_t)**alpha_xi  # Eqn 8.12-9
    else:
        Xi_SBHeHo = Xi_th  # Eqn 8.12-9
    Xi_SBHeHo = max(Xi_SBHeHo, Xi_3LM) # Eqn 8.12-9

    f = 4./3. - (1./3.)*(d/Dp)/particle_ratio # Eqn 8.12-10 TODO: update with dynamic particle ratio in section 7.7.5
    f = min(max(f, 0), 1)
    Xi_SF = Xi_SBHeHo * f + Xi_3LM*(1-f)    # Eqn 8.12-11
    return Xi_SF

def Cvs_from_Cvt(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvt):
    """
    Cvs_from_Cvt - Calculate the Cvs for the given Cvt
    vls = average line speed (velocity, m/sec)
    Dp = Pipe diameter (m)
    d = Particle diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cvt = transported volume concentration
    get_dict: if true return the dict with all models.
    """
    Xi = slip_ratio(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt)
    return (1/(1-Xi)) * Cvt # Eqn 8.12-12


def Cvt_Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvt, get_dict=False):
    """
    Cvt_Erhg - Calculate the Erhg for the given Cvt, using the appropriate model
    vls = average line speed (velocity, m/sec)
    Dp = Pipe diameter (m)
    d = Particle diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cvt = transported volume concentration
    get_dict: if true return the dict with all models.
    """
    Cvs = Cvs_from_Cvt(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt)
    Xi = slip_ratio(vls, Dp, d, epsilon, nu, rhol, rhos, Cvt)
    Erhg_obj = Cvs_Erhg(vls, Dp, d, epsilon, nu, rhol, rhos, Cvs, get_dict=True)
    for regime in ["FB", "SB", "He", "Ho"]:
        Erhg_obj[regime] = Erhg_obj[regime]*1/(1-Xi)    # Eqn 8.12-12
    if Erhg_obj['regime'] == "FB":
        # Use min of SB, He if in fixed bed region, text after Eqn 8.12-12
        if Erhg_obj["SB"] < Erhg_obj["He"]:
            Erhg_obj['regime'] = "SB"
        else:
            Erhg_obj['regime'] = "He"
    Erhg_obj['Xi'] = Xi
    if get_dict:
        return Erhg_obj
    else:
        return Erhg_obj[Erhg_obj['regime']]


def Cvt_regime(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvt):
    """
    Return the name of the regime for the given slurry and velocity in the Cvt case
    vls = average line speed (velocity, m/sec)
    Dp = Pipe diameter (m)
    d = Particle diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cvs = insitu volume concentration
    """
    Erhg_obj = Cvt_Erhg(vls, Dp,  d, epsilon, nu, rhol, rhos, Cvt, get_dict=True)
    return {'FB': 'fixed bed',
            'SB': 'sliding bed',
            'He': 'heterogeneous',
            'Ho': 'homogeneous',
            }[Erhg_obj['regime']]


def pseudo_dlim(Dp, nu, rhol, rhos):
    """
    Return the maximum particle diameter that affects the pseudoliquid
    Dp = Pipe diameter (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    """

    dlim = (stk_fine*9.*rhol*nu*Dp / (rhos*7.5*Dp**0.4))**0.5 # Eqn 8.15-2
    return dlim

def create_fracs(GSD, Dpo, nu, rhol, rhos, num_fracs=10):
    """Divide the GSD into at least num_fracs fractions

    Start by determining the dlim
    Add the points for dia greater than the dlim (points less than dlim are discarded)
    interpolate points between the given points until at least at num_fracs-1
    Extrapolate one point above the maximum fraction"""
    new_GSD = {}
    fracs = iter(sorted(GSD, key=lambda key: GSD[key]))
    flow = next(fracs)
    dlow = GSD[flow]
    fnext = next(fracs)
    dnext = GSD[fnext]
    points_left = len(fracs)

    Rsd = (rhos - rhol) / rhol  # Eqn 8.2-1

    # The limiting diameter for pseudoliquid and it's fraction X
    dmin = pseudo_dlim(Dp, nu, rhol, rhos)
    while dmin > dnext:
        ftemp = next(fracs, None)
        if ftemp:
            dlow = dnext
            flow = fnext
            fnext = ftemp
            dnext = GSD[fnext]
            points_left -= 1
        else:
            break
    X = fnext - (log10(dnext) - log10(dmin)) * (fnext - flow) / (log10(dnext) - log10(dlow))
    if X < 0:
        X = 0
    new_GSD[X] = dmin
    num_divs = num_fracs - points_left - 1
    between_points = int(num_divs/points_left + 0.5)

    flow = X
    dlow = dmin
    while fnext:
        frac_size = (fnext - flow) / (between_points + 1)
        dnext = GSD[fnext]
        fthis = flow
        for i in range(1, between_points+1):
            flow += frac_size
            logdlast = log10(dast)
            logdthis = log10(dnext) - (log10(dnext) - log10(dlow)) * (fnext - fthis) / (fnext - flow)
            new_GSD[fthis] = dlow = 10**logdthis
        flow = fnext
        dlow = GSD[flow]
        fnext = next(fracs, None)
    fnext = max(new_GSD.keys())
    dnext = new_GSD[fnext]
    fthis = min(fnext + frac_size, 0.999)
    logdthis = log10(dnext) - (log10(dnext) - log10(dlow)) * (fnext - fthis) / (fnext - flow)
    new_GSD[fthis] = 10 ** logdthis
    return new_GSD

def Erhg_graded(GSD, vls, Dp, epsilon, nu, rhol, rhos, Cv, Cvt_eq_Cvs=False, num_fracs=10, get_dict=False):
    """
    Erhg_graded - Calculate the Erhg for the given slurry, using the appropriate model
    GSD = Particle size distribution dict: {x:d_x, y:d_y, ...}, len(GSD>2)
    vls = average line speed (velocity, m/sec)
    Dp = Pipe diameter (m)
    epsilon = absolute pipe roughness (m)
    nu = fluid kinematic viscosity in m2/sec
    rhol = density of the fluid (ton/m3)
    rhos = particle density (ton/m3)
    Cv = insitu volume concentration
    num_fracs = The number of fractions to divide the GSD
    get_dict: Does nothing for now
    """
    fracs = iter(sorted(GSD, key=lambda key: GSD[key]))
    flow = next(fracs)
    dlow = GSD[flow]
    fnext = next(fracs)
    dnext = GSD[fnext]

    Rsd = (rhos - rhol) / rhol  # Eqn 8.2-1

    # The limiting diameter for pseudoliquid and it's fraction X
    dmin = pseudo_dlim(Dp, nu, rhol, rhos)
    while dmin > dnext:
        ftemp = next(fracs, None)
        if ftemp:
            dlow = dnext
            flow = fnext
            fnext = ftemp
            dnext = GSD[fnext]
        else:
            break
    X = fnext - (log10(dnext)-log10(dmin))*(fnext-flow)/(log10(dnext)-log10(dlow))
    if X < 0:
        X = 0
    rhox = rhol + rhol*(X*Cv*Rsd)/(1-Cv+Cv*X)    # Eqn 8.15-3
    Cv_x = (X*Cv)/(1-Cv+Cv*X)
    Cv_r = (1 - X) * Cv                           # Eqn 8.15-5
    mu_l = nu * rhol
    mu_x = mu_l*(1 + 2.5*Cv_x + 10.05*Cv_x**2 + 0.00273*exp(16.6*Cv_x))   # Eqn 8.15-6
    nu_x = mu_x / rhox                              # Eqn 8.15-7
    Rsd_x = (rhos - rhox)/rhox

    frac_size = (1.0 - X)/(num_fracs)
    ims = []  # This will be a list of the fi, i_mxi
    fthis = X
    logdlast = log10(dmin)
    frac_list = [fthis]
    ds = [10**logdlast]                 #These are the boundaries of the fractions
    dxs = []                            #These are the central diameter of the fractions
    while fthis <= (1.0 - frac_size):
        fthis += frac_size
        while fthis > fnext:
            ftemp = next(fracs, None)
            if ftemp:
                dlow = dnext
                flow = fnext
                fnext = ftemp
                dnext = GSD[fnext]
            else:
                break
        logdthis = log10(dnext) - (log10(dnext)-log10(dlow))*(fnext-fthis)/(fnext-flow)
        logdx = (logdthis + logdlast)/2.0
        logdlast = logdthis
        dx = 10**logdx
        if Cvt_eq_Cvs:
            Erhg_x = Cvt_Erhg(vls, Dp, dx, epsilon, nu_x, rhox, rhos, Cv_r, get_dict=True)
        else:
            Erhg_x = Cvs_Erhg(vls, Dp, dx, epsilon, nu_x, rhox, rhos, Cv_r, get_dict=True)
        regime = Erhg_x['regime']
        il_x = Erhg_x['il']
        i_mxi = Erhg_x[regime] * Rsd_x * Cv_r + il_x
        frac_list.append(fthis)
        ds.append(10.0**logdthis)
        dxs.append(dx)
        ims.append(i_mxi)
    im_x = sum(frac_size*imxi for imxi in ims)/ (1-X)
    il_x = homogeneous.fluid_head_loss(vls, Dp, epsilon, nu_x, rhox)
    im = rhox*im_x/rhol
    il = homogeneous.fluid_head_loss(vls, Dp, epsilon, nu, rhol)
    Erhg = (im - il)/(Rsd*Cv)
    if get_dict:
        return {'ims': ims, 'im_x': im_x, 'Erhg_x': (im_x - il_x)/(Rsd_x*Cv_r),
                'Erhg': Erhg, 'il': il,
                'dmin': dmin, 'X': X, 'fracs': frac_list, 'ds': ds, 'dxs': dxs,
                'mu_x': mu_x, 'nu_x': nu_x, 'rhox': rhox, 'Rsd_x': Rsd_x, 'Cv_x': Cv_x, 'Cv_r': Cv_r,
                }
    else:
        return Erhg


if __name__ == '__main__':
    pass
