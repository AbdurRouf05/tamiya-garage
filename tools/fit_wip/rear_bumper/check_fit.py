"""Interference/gap check of rear bumper vs chassis at a given translation, fine voxels.
python check_fit.py dx dy dz [h]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slicer import transformed
from voxel import voxelize
import numpy as np
from scipy.ndimage import label, binary_dilation, distance_transform_edt
dx, dy, dz = (float(v) for v in sys.argv[1:4]); h = float(sys.argv[4]) if len(sys.argv) > 4 else 0.1
J = 0.00731
rb = transformed("chassis-super-1-rear-bumper") + np.array([dx, dy, dz])
lo = rb.reshape(-1, 3).min(0) - 1.5; hi = rb.reshape(-1, 3).max(0) + 1.5
org = np.floor(lo / h) * h + J
shape = tuple(np.ceil((hi - org) / h).astype(int))
ch = transformed("chassis-super-1")
c = ch.mean(1); ch = ch[np.all((c > lo - 3) & (c < hi + 3), axis=1)]
C = voxelize(ch, org, h, shape); B = voxelize(rb, org, h, shape)
ov = C & B
print(f"shift ({dx},{dy},{dz}) h={h}: bumper vol {B.sum()*h**3:.1f} mm3, overlap {ov.sum()*h**3:.3f} mm3")
lab, n = label(ov)
comps = []
for i in range(1, n + 1):
    idx = np.argwhere(lab == i)
    p = org + (idx + 0.5) * h
    comps.append((len(idx) * h**3, p.min(0), p.max(0)))
comps.sort(key=lambda q: -q[0])
for v, a, b in comps[:12]:
    print(f"   overlap blob {v:7.3f} mm3  X {a[0]:.2f}..{b[0]:.2f}  Y {a[1]:.2f}..{b[1]:.2f}  Z {a[2]:.2f}..{b[2]:.2f}")
# contact (gap <= 1 voxel) and near-gaps
d = distance_transform_edt(~C) * h   # distance from each voxel to chassis
bd = d[B]
print(f"bumper voxels within 0.15 mm of chassis: {np.sum(bd <= 0.15)*h**3:.2f} mm3; within 0.3: {np.sum(bd <= 0.3)*h**3:.2f}")
np.savez_compressed(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit_%g_%g_%g.npz" % (dx, dy, dz)), C=C, B=B, org=org, h=h)
