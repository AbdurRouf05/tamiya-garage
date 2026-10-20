import numpy as np
from common import *
from vox import *
from scipy import ndimage
g = Grid([0, 0, 3], [80, 136, 33], 0.2)
L = lambda k: np.unpackbits(np.load(f"cache/occ02_{k}.npy"))[:np.prod(g.shape)].reshape(g.shape).astype(bool)
ch, br = L("chassis"), L("motor_bracket")
ov = ch & br
lab, n = ndimage.label(ov)
print("components", n)
for i in range(1, n + 1):
    w = np.argwhere(lab == i)
    if len(w) < 20: continue
    p = w * 0.2 + g.lo + 0.1
    print(f"  comp {i}: {len(w)*0.008:6.2f} mm3  X {p[:,0].min():.1f}..{p[:,0].max():.1f}  Y {p[:,1].min():.1f}..{p[:,1].max():.1f}  Z {p[:,2].min():.1f}..{p[:,2].max():.1f}")
