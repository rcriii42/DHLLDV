if __name__ == '__main__':
    print("Running LSLDV.py")
    import DHLLDV.DHLLDV_constants as const
    import  DHLLDV.stratified as strat
    Dp = 0.762  # Pipe diameter
    d = 1 / 1000.
    epsilon = const.steel_roughness
    nu = const.water_viscosity[20]
    rhos = 2.65
    rhol = const.water_density[20]
    Rsd = (rhos - rhol) / rhol
    Cv = 0.175
    rhom = Cv * (rhos - rhol) + rhol
    print(f"{'diameter':8s} {'v: 10% conc':11s} {'v: 17.5% conc':12s} {'v: 20% conc':11s} {'v: 30% conc':11s}")
    print(f"{'mm':>8s} {'m/sec':>11s} {'m/sec':>12s} {'m/sec':>11s} {'m/sec':>11s}")
    for d in [0.1, 0.2, 0.4, 0.8, 1.0, 2, 4, 8, 16, 32]:
        v1, v2, v3, v4 = (strat.vls_FBSB(Dp, d/1000, epsilon, nu, rhol, rhos, Cv) for Cv in [0.1, 0.175, 0.2, 0.3])
        if d ==1:   # call out the diameter/conc that coincides with the default in viewer
            print("....")
        print(f"{d:8.2f} {v1:11.3f} {v2:12.3f} {v3:11.3f} {v4:11.3f}")
        if d ==1:
            print("....")

