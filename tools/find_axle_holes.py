"""Cari lubang bearing as roda di dinding sasis Super-1 (mm, koordinat STL asli).

python tools/find_axle_holes.py
Lubang = cakram kosong (tidak ada titik di dalam jari-jari 2,4 mm) yang dikelilingi cincin titik
di jari-jari 2,95 mm (diameter luar bearing 5,9 mm), dicari di irisan dinding tempat bearing duduk.
"""
import struct
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parent.parent / "models" / "source" / "super1-printables"


def verts(name):
    data = (SRC / name).read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    tri = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    return np.unique(tri["v"].reshape(-1, 3).round(3), axis=0)


v = verts("chassis-super-1.stl")
for xc in (59.7, 78 - 59.7):
    s = v[np.abs(v[:, 0] - xc) < 1.2][:, 1:]
    best = []
    for y in np.arange(5, 120, 0.25):
        col = s[np.abs(s[:, 0] - y) < 3.4]
        if len(col) < 6:
            continue
        for z in np.arange(8, 22, 0.25):
            d = np.hypot(col[:, 0] - y, col[:, 1] - z)
            inside, ring = np.sum(d < 2.4), np.sum(np.abs(d - 2.95) < 0.25)
            if inside == 0 and ring >= 10:
                best.append((ring, y, z))
    best.sort(reverse=True)
    picked = []
    for ring, y, z in best:
        if all(abs(y - py) > 6 or abs(z - pz) > 6 for _, py, pz in picked):
            picked.append((ring, y, z))
    print(f"dinding x≈{xc:.1f}:", ", ".join(f"(y={y:.2f}, z={z:.2f}, cincin {r})" for r, y, z in picked[:5]))
