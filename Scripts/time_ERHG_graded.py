import timeit
import cProfile
from pstats import SortKey

from DHLLDV.SlurryObj import Slurry

def ex_slurry():
    s = Slurry()
    out_head = []
    for d in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]:
        s.D50 = d
        out_head.append(s.im_curves['graded_Cvt_im'][42])
    return out_head

print(timeit.timeit(ex_slurry, number=10))

with cProfile.Profile() as pr:
    _ = ex_slurry()
pr.print_stats(SortKey.CUMULATIVE)
