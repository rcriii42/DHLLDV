'''
DHLLDV_Utils: Utility functions.

Created on Oct 23, 2014

@author: RCRamsdell
'''
import bisect

class interpDict(dict):
    """
    interpDict: Dict of two-tuples that will interpolate values not found in the dict.
    """
    def __init__(self, *args):
        #print type(args[0]), args
        if type(args[0])==type(dict()):
            self.update(args[0])
        else:
            dict.__init__(self, args)

    def __getitem__(self, key):
        try:
            val = dict.__getitem__(self, key)
        except KeyError:
            keys = sorted(self.keys())
            index = bisect.bisect(keys, key)
            if index and index!=len(keys):
                x1 = keys[index-1]
                x2 = keys[index]
                y1 = dict.__getitem__(self, x1)
                y2 = dict.__getitem__(self, x2)
                val = ((y2-y1)/(x2-x1))*(key-x1)+y1
            else:
                if key > max(keys):
                    bound = f" max {max(keys)}"
                else:
                    bound = f" min {min(keys)}"
                raise IndexError(f"Key {key} out of range ({bound})")
        return val

    def __setitem__(self, key, val):
        raise KeyError("interpDict is read-only")