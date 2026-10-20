import numpy as np, common
from scipy import ndimage
g = common.Grid()
def load(p): return np.unpackbits(np.load(common.CACHE / f"occ_{p}.npy"))[: g.n.prod()].reshape(g.n).astype(bool)
ch, gc, mb = load("chassis"), load("gear-cover"), load("motor-bracket")
for nm, a, b in (("bracket&chassis", mb, ch), ("cover&chassis", gc, ch), ("cover&bracket", gc, mb)):
    o = a & b
    print(nm, "voxels", o.sum(), "vol mm3", round(o.sum() * g.h**3, 2))
    lab, n = ndimage.label(o)
    for i, sl in enumerate(ndimage.find_objects(lab)):
        cnt = (lab[sl] == i + 1).sum()
        if cnt < 5: continue
        lo = [g.lo[k] + sl[k].start * g.h for k in range(3)]; hi = [g.lo[k] + sl[k].stop * g.h for k in range(3)]
        print(f"   blob {cnt:6d} vox  X {lo[0]:.1f}..{hi[0]:.1f}  Y {lo[1]:.1f}..{hi[1]:.1f}  Z {lo[2]:.1f}..{hi[2]:.1f}")
