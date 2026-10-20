import numpy as np
from common import *
d = np.load("cache/fa130.npz"); v = d["fa130__v"] / S  # mm, glb axes, shaft along -z
print("bbox mm", v.min(0).round(2), v.max(0).round(2))
for z0 in np.arange(-19.5, 19.5, 1.0):
    m = (v[:, 2] >= z0) & (v[:, 2] < z0 + 1)
    if m.any():
        w = v[m]; r = np.hypot(w[:, 0], w[:, 1])
        print(f"z {z0:6.1f}..{z0+1:5.1f}: n={m.sum():6d} x {w[:,0].min():6.2f}..{w[:,0].max():6.2f}  y {w[:,1].min():6.2f}..{w[:,1].max():6.2f}  rmax {r.max():5.2f} rmin {r.min():5.2f}")
