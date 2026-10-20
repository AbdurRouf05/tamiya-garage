import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slicer import transformed
from voxel import voxelize
import numpy as np
h = 0.25
J = 0.0123
t = transformed("chassis-super-1-rear-bumper")
mn = t.reshape(-1, 3).min(0) - 1 + J; mx = t.reshape(-1, 3).max(0) + 1
shape = tuple(np.ceil((mx - mn) / h).astype(int))
t0 = time.time(); occ = voxelize(t, mn, h, shape); print("bumper", shape, occ.sum() * h**3, "mm3", time.time() - t0)
# sanity: check column parity issues: count columns where occupancy reaches top layer
print("top layer occupied (should be 0):", occ[:, :, -1].sum(), occ[:, :, 0].sum())
