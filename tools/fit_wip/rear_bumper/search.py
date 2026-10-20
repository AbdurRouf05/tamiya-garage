"""FFT search of all integer-voxel translations of the rear bumper against the chassis.
Reports overlap volume (interpenetration) and contact (bumper voxels in a 1-voxel shell around chassis)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slicer import transformed
from voxel import voxelize
import numpy as np
from scipy.signal import fftconvolve
from scipy.ndimage import binary_dilation
W = os.path.dirname(os.path.abspath(__file__))
h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
J = 0.0123
corg = np.array([-3.0, 66.0, 1.0]) + J
cshape = tuple(np.ceil((np.array([81.0, 125.0, 22.0]) - corg) / h).astype(int))
ch = transformed("chassis-super-1")
ch = ch[(ch[:, :, 1] > 60).any(1)]
t0 = time.time(); C = voxelize(ch, corg, h, cshape); print("chassis vox", cshape, C.sum() * h**3, time.time() - t0)
rb = transformed("chassis-super-1-rear-bumper")
rmn = rb.reshape(-1, 3).min(0) - 1
borg = corg + np.floor((rmn - corg) / h) * h
bshape = tuple(np.ceil((rb.reshape(-1, 3).max(0) + 1 - borg) / h).astype(int))
B = voxelize(rb, borg, h, bshape); print("bumper vox", bshape, B.sum() * h**3)
np.savez_compressed(os.path.join(W, f"vox_{h}.npz"), C=C, B=B, corg=corg, borg=borg, h=h)
shell = binary_dilation(C, iterations=1) & ~C
Bf = B[::-1, ::-1, ::-1].astype(np.float32)
ov = fftconvolve(C.astype(np.float32), Bf, mode="full")
ct = fftconvolve(shell.astype(np.float32), Bf, mode="full")
# full index m corresponds to shift s (voxels) where bumper voxel q maps to chassis voxel q + off + s ; off = (borg-corg)/h
off = np.round((borg - corg) / h).astype(int)
# conv full: out[m] = sum_q C[m - (bshape-1) + q] B[q]  => chassis index = q + m - (bshape-1) => s = m - (bshape-1) - off
sh = np.array(bshape) - 1 + off
np.savez_compressed(os.path.join(W, f"corr_{h}.npz"), ov=ov.astype(np.float32), ct=ct.astype(np.float32), sh=sh)
def at(s):
    m = tuple(np.array(s) + sh)
    return ov[m] * h**3, ct[m] * h**3
print("file position: overlap mm3=%.2f contact=%.2f" % at((0, 0, 0)))
print("file+X1: overlap=%.2f contact=%.2f" % at((round(1 / h), 0, 0)))
# candidates in range
rng = dict(x=(-8, 8), y=(-25, 30), z=(-16, 12))
idx = np.indices(ov.shape).reshape(3, -1).T
s = idx - sh
m = ((s[:, 0] * h >= rng["x"][0]) & (s[:, 0] * h <= rng["x"][1]) & (s[:, 1] * h >= rng["y"][0]) & (s[:, 1] * h <= rng["y"][1]) & (s[:, 2] * h >= rng["z"][0]) & (s[:, 2] * h <= rng["z"][1]))
o = ov.reshape(-1)[m] * h**3; c = ct.reshape(-1)[m] * h**3; ss = s[m] * h
for thr in (0.5, 2.0, 5.0):
    k = np.nonzero(o <= thr)[0]
    best = k[np.argsort(-c[k])[:15]]
    print(f"--- overlap <= {thr} mm3, top contact:")
    for b in best:
        print(f"  d=({ss[b,0]:6.2f},{ss[b,1]:6.2f},{ss[b,2]:6.2f})  overlap={o[b]:7.2f}  contact={c[b]:7.2f}")
