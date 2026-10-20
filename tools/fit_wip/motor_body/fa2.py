import numpy as np
from common import *
d = np.load("cache/fa130.npz"); v = d["fa130__v"] / S; f = d["fa130__f"]
t = v[f]  # triangles
# fine profile of max radius from triangles sampled (use triangle centroids + vertices)
r = np.hypot(v[:, 0], v[:, 1])
for z0 in np.arange(-19.25, 19.5, 0.5):
    m = (v[:, 2] >= z0) & (v[:, 2] < z0 + 0.5)
    if m.any():
        print(f"z {z0:6.2f}: n={m.sum():5d} rmax {r[m].max():5.2f} rmin {r[m].min():5.2f}  y {v[m,1].min():6.2f}..{v[m,1].max():6.2f}")
# triangles spanning long in z near axis (shaft)
zz = t[:, :, 2]; rr = np.hypot(t[:, :, 0], t[:, :, 1])
long = (zz.max(1) - zz.min(1) > 3) & (rr.max(1) < 1.3)
print("long thin tris near axis:", long.sum(), "z ranges", np.unique(np.round(np.c_[zz[long].min(1), zz[long].max(1)], 1), axis=0)[:20])
