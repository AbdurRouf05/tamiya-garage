import numpy as np, sys
from scipy import ndimage
from vox import Grid
g = Grid([14, -1, 3], [64, 36, 24], 0.1)
z = np.load(sys.argv[1])
a, b = sys.argv[2], sys.argv[3]
o = z[a] & z[b]
lab, n = ndimage.label(o)
print(f"{a}&{b}: total {o.sum()*1e-3:.2f} mm3, {n} regions")
for i in range(1, n + 1):
    idx = np.argwhere(lab == i)
    if len(idx) < 20: continue
    P0 = g.lo + idx.min(0) * g.h - g.h/2; P1 = g.lo + idx.max(0) * g.h + g.h/2
    print(f"  region {i}: {len(idx)*1e-3:.2f} mm3  X {P0[0]:.2f}..{P1[0]:.2f}  Y {P0[1]:.2f}..{P1[1]:.2f}  Z {P0[2]:.2f}..{P1[2]:.2f}")
