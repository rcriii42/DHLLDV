'''
DHLLDV_Utils: Utility functions.

Created on Oct 23, 2014

@author: RCRamsdell
'''
import bisect


class interpDict(dict):
    """
    interpDict: Dict of two-tuples that will interpolate values not found in the dict.

    The key/value pairs are floats x, f(x), assumes f(x) is continuous on the bounds of x, sorted on x low to high
    extrapolate_low: True if the interpolation should be continued below the low end of the range (default=False)
    extrapolate_high: True if the interpolation should be continued above the high end of the range (default=False)
    tolerance: By how much x is allowed to exceed the top or bottom end
    """
    def __init__(self, *args, **kwargs):
        if type(args[0]) == type(dict()):
            self.update(args[0])
        else:
            dict.__init__(self, args)
        self.extrapolate_low = kwargs.setdefault('extrapolate_low', False)
        self.extrapolate_high = kwargs.setdefault('extrapolate_high', False)
        self.tolerance = kwargs.setdefault('tolerance', 0.001)

    def __getitem__(self, key):
        try:
            val = dict.__getitem__(self, key)
        except KeyError:
            keys = sorted(self.keys())
            index = bisect.bisect(keys, key)
            if index and index != len(keys):
                x1 = keys[index-1]
                x2 = keys[index]
                y1 = dict.__getitem__(self, x1)
                y2 = dict.__getitem__(self, x2)
                val = ((y2-y1)/(x2-x1))*(key-x1)+y1
            elif index == len(keys) and (self.extrapolate_high or key <= max(keys)*(1+self.tolerance)):
                x1 = keys[-2]
                x2 = keys[-1]
                y1 = dict.__getitem__(self, x1)
                y2 = dict.__getitem__(self, x2)
                val = ((y2 - y1) / (x2 - x1)) * (key - x1) + y1
            elif index == 0 and (self.extrapolate_low or key >= min(keys)*(1-self.tolerance)):
                x1 = keys[0]
                x2 = keys[1]
                y1 = dict.__getitem__(self, x1)
                y2 = dict.__getitem__(self, x2)
                val = ((y2 - y1) / (x2 - x1)) * (key - x1) + y1
            else:
                bounds = f"{min(keys)} - {max(keys)}"
                raise IndexError(f"Key {key} out of range ({bounds})")
        return val

    def __setitem__(self, key, val):
        raise KeyError("interpDict is read-only")
