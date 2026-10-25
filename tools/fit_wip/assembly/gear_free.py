"""Jari-jari bebas di sekitar tiap poros gear per irisan X (jarak ke permukaan part terdekat pada potongan bidang X).
Pakai segmen potongan (permukaan), jadi tidak bergantung pada mesh yang rapat. python gear_free.py [x0 x1 dx]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rear_bumper"))
from slicer import transformed, section
import numpy as np

T0 = np.array([0.977, 13.96, 0.0])
x0, x1, dx = (float(v) for v in sys.argv[1:4]) if len(sys.argv) > 3 else (17.0, 33.0, 0.25)
ch = transformed("chassis-super-1")
P = {"sasis": ch[(ch[:, :, 1].max(1) > 84)], "dudukan": transformed("chassis-super-1-motor-bracket") + T0,
     "gearcover": transformed("chassis-super-1-gear-cover") + T0}
P = {k: (t, t[:, :, 0].min(1), t[:, :, 0].max(1)) for k, t in P.items()}
C = {"pinion": ((100.32, 17.69), 1.2), "counter": ((104.30, 23.92), 1.0), "spur": ((108.515, 15.095), 1.15)}

def segdist(seg, p):
    a, b = seg[:, 0], seg[:, 1]; ab = b - a; ap = p - a
    t = np.clip((ap * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-12), 0, 1)
    return np.hypot(*(a + ab * t[:, None] - p).T)

print("X      " + "  ".join(f"{k:>18s}" for k in C))
for X in np.arange(x0, x1 + 1e-9, dx):
    row = []
    segs = {k: section(t[(lo <= X) & (hi >= X)], "x", X)[:, :, 1:] for k, (t, lo, hi) in P.items()}
    for nm, (c, rmin) in C.items():
        best = (99.0, "-")
        for k, s in segs.items():
            if not len(s): continue
            d = segdist(s, np.array(c)); d = d[d > rmin]
            if len(d) and d.min() < best[0]: best = (d.min(), k)
        row.append(f"{best[0]:6.2f} {best[1]:>10s}")
    print(f"{X:5.2f}  " + "  ".join(f"{r:>18s}" for r in row))
