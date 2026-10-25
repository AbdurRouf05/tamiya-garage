"""Interference/gap check of a Super-1 part vs chassis (or another part) at a given translation, fine voxels.
python check_fit.py [part] dx dy dz [h] [lawan]     part default rear-bumper, lawan default chassis
(lawan = nama part lain, ikut digeser dx,dy,dz juga, untuk cek antar-part setelah koreksi)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slicer import transformed
from voxel import voxelize
import numpy as np
from scipy.ndimage import label, distance_transform_edt
a = sys.argv[1:]
part = a.pop(0) if a and not a[0].lstrip("+-").replace(".", "", 1).isdigit() else "rear-bumper"
dx, dy, dz = (float(v) for v in a[0:3]); h = float(a[3]) if len(a) > 3 else 0.1
other = a[4] if len(a) > 4 else None
J = 0.00731
rb = transformed("chassis-super-1-" + part) + np.array([dx, dy, dz])
lo = rb.reshape(-1, 3).min(0) - 1.5; hi = rb.reshape(-1, 3).max(0) + 1.5
org = np.floor(lo / h) * h + J
shape = tuple(np.ceil((hi - org) / h).astype(int))
ch = transformed("chassis-super-1-" + other) + np.array([dx, dy, dz]) if other else transformed("chassis-super-1")
# potong hanya di XY: segitiga di atas/bawah grid tetap dipakai agar paritas sinar Z benar
mn = ch[:, :, :2].min(1); mx = ch[:, :, :2].max(1); ch = ch[np.all((mx > lo[:2] - 3) & (mn < hi[:2] + 3), axis=1)]
C = voxelize(ch, org, h, shape); B = voxelize(rb, org, h, shape)
ov = C & B
print(f"{part} vs {other or 'chassis'} shift ({dx},{dy},{dz}) h={h}: part vol {B.sum()*h**3:.1f} mm3, overlap {ov.sum()*h**3:.3f} mm3")
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
print(f"part voxels within 0.15 mm of {other or 'chassis'}: {np.sum(bd <= 0.15)*h**3:.2f} mm3; within 0.3: {np.sum(bd <= 0.3)*h**3:.2f}")
