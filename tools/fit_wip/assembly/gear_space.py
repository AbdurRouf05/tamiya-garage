"""Ruang bebas untuk gear (pinion di sumbu dinamo, counter di porosnya, spur di as belakang) setelah koreksi T0.
Voxel semua part di zona gear, lalu untuk tiap jari-jari calon dan tiap irisan X hitung voxel part di dalam piringan.
python gear_space.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rear_bumper"))
from slicer import transformed
from voxel import voxelize
import numpy as np


def voxelize3(t, org, h, shape):
    """Voting mayoritas sinar Z, X, dan Y: gear cover tidak rapat, jadi paritas satu arah saja bisa bocor."""
    votes = voxelize(t, org, h, shape).astype(np.uint8)
    for perm in ((1, 2, 0), (2, 0, 1)):
        inv = np.argsort(perm)
        o = voxelize(t[:, :, perm], np.asarray(org)[list(perm)], h, tuple(np.array(shape)[list(perm)]))
        votes += o.transpose(inv)
    return votes >= 2

T0 = np.array([0.977, 13.96, 0.0])
h = 0.2
org = np.array([15.0, 84.0, 2.0]) + np.array([0.00731, 0.00517, 0.00293])
shape = (100, 200, 165)
hi = org + np.array(shape) * h
occ = np.zeros(shape, bool)
for n, sh in [("chassis-super-1", 0), ("chassis-super-1-motor-bracket", 1), ("chassis-super-1-gear-cover", 1), ("chassis-super-1-rear-bumper", 1)]:
    t = transformed(n) + (T0 if sh else 0)
    mn = t[:, :, :2].min(1); mx = t[:, :, :2].max(1)
    t = t[np.all((mx >= org[:2]) & (mn <= hi[:2]), axis=1)]
    occ |= voxelize3(t, org, h, shape)
X = org[0] + (np.arange(shape[0]) + 0.5) * h
Y = org[1] + (np.arange(shape[1]) + 0.5) * h
Z = org[2] + (np.arange(shape[2]) + 0.5) * h
GY, GZ = np.meshgrid(Y, Z, indexing="ij")
G = {"pinion": ((100.32, 17.69), [1.8, 2.0, 2.2, 2.4, 2.6]),
     "counter": ((104.30, 23.92), [2.5, 3.0, 4.0, 5.0, 5.4, 5.8, 6.2]),
     "spur": ((108.515, 15.095), [5.0, 6.0, 7.0, 7.5, 8.0, 8.5, 9.0])}
for nm, ((cy, cz), rs) in G.items():
    d = np.hypot(GY - cy, GZ - cz)
    print(f"== {nm} di (Y{cy}, Z{cz}): rentang X tanpa tabrakan (voxel 0,2 mm, abaikan r < 1,2 = poros)")
    for r in rs:
        disk = (d <= r) & (d >= 1.2)
        hit = np.array([(occ[i] & disk).sum() for i in range(shape[0])])
        free = hit == 0
        runs, i = [], 0
        while i < len(free):
            if free[i]:
                j = i
                while j + 1 < len(free) and free[j + 1]: j += 1
                if X[j] - X[i] >= 0.6: runs.append(f"{X[i]-h/2:.1f}..{X[j]+h/2:.1f}")
                i = j + 1
            else: i += 1
        print(f"   r={r:4.1f}: " + ("  ".join(runs) if runs else "-"))
