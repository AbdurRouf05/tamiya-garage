import numpy as np
from common import *
from slicer import slice_tris
d = np.load("cache/fa130.npz"); v = d["fa130__v"] / S; f = d["fa130__f"]; t = v[f]
# Use slices (exact cross sections) of the triangle mesh along z
for z in list(np.arange(-19.0, -14.0, 0.1)) + list(np.arange(8.6, 12.0, 0.1)) + [18.9, 19.0]:
    s = slice_tris(t, 2, z).reshape(-1, 3)
    if len(s) == 0:
        print(f"z={z:6.2f}: empty"); continue
    r = np.hypot(s[:, 0], s[:, 1])
    print(f"z={z:6.2f}: rmax {r.max():5.2f}  x {s[:,0].min():6.2f}..{s[:,0].max():6.2f}  y {s[:,1].min():6.2f}..{s[:,1].max():6.2f}")
