import numpy as np, time
from common import *
from vox import *
g = Grid([0, 0, 3], [80, 136, 33], 0.2)
print("grid", g.shape)
occ = {}
for k in ["chassis", "motor_bracket", "gear_cover", "rear_bumper", "switch_cover", "battery_retainer", "switch_knob"]:
    t0 = time.time()
    o, nodd, ncol = solid(part(PARTS[k]), g, return_odd=True)
    occ[k] = o
    np.save(f"cache/occ02_{k}.npy", np.packbits(o))
    print(f"{k:16s} vox={o.sum():9d} vol={o.sum()*0.008:8.1f} mm3 odd cols {nodd}/{ncol}  {time.time()-t0:.1f}s")
ks = list(occ)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        n = (occ[ks[i]] & occ[ks[j]]).sum()
        if n:
            w = np.argwhere(occ[ks[i]] & occ[ks[j]]) * 0.2 + g.lo + 0.1
            print(f"  overlap {ks[i]} x {ks[j]}: {n} vox = {n*0.008:.1f} mm3, bbox {w.min(0).round(1)}..{w.max(0).round(1)}")
