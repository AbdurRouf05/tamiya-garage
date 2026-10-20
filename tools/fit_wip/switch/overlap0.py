import numpy as np, time
from load import tris
from vox import Grid, voxelize
g = Grid([14, -1, 3], [64, 36, 24], 0.1)
t0 = time.time()
ch = voxelize(tris("chassis-super-1.stl"), g); print("chassis", ch.sum() * 1e-3, "mm3", time.time() - t0)
cv = voxelize(tris("chassis-super-1-switch-cover.stl"), g); print("cover", cv.sum() * 1e-3)
kn = voxelize(tris("chassis-super-1-switch-on-off.stl"), g); print("knob", kn.sum() * 1e-3)
np.savez_compressed("cache/vox_file.npz", ch=ch, cv=cv, kn=kn)
for a, b, nm in ((ch, cv, "chassis&cover"), (ch, kn, "chassis&knob"), (cv, kn, "cover&knob")):
    o = a & b
    print(nm, "overlap mm3", o.sum() * 1e-3)
    if o.any():
        idx = np.argwhere(o)
        P = g.lo + idx * g.h
        print("   bbox", P.min(0).round(2), P.max(0).round(2))
