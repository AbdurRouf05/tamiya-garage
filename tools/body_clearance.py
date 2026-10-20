"""Cek part dalam yang menembus body (Super-1 + body sayap), dalam satuan simulator.

python tools/body_clearance.py [naik_y] [skala_x] [skala_y] [skala_z]

Body diubah menjadi peta ketinggian (tinggi permukaan atas per sel x-z). Titik part
dianggap menembus jika berada di bawah tapak body tetapi lebih tinggi dari permukaannya.
"""
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent / "models" / "source"
S = 0.1346          # mm -> satuan simulator
R = 1.75            # jari-jari roda kecil = tinggi as roda
CELL = 0.25
lift = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
sx, sy, sz = (float(a) for a in sys.argv[2:5]) if len(sys.argv) > 4 else (1.0, 1.0, 1.0)


def stl(path):
    data = path.read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    tri = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    return tri["v"].reshape(-1, 3).astype(np.float64)


def super1(name):
    """Sama dengan transform Blender: geser ke as roda, putar 90 derajat, skala, lalu ke Y-atas glTF."""
    v = stl(ROOT / "super1-printables" / f"chassis-super-1{name}.stl") - [39, 70, 15.1]
    x, y, z = -v[:, 1] * S, v[:, 2] * S + R, -v[:, 0] * S
    return np.column_stack([x, y, z])


# Body: asal (4.5,0,0), skala, diputar 180 derajat, geser (-0.15, 0.4)
b = stl(ROOT / "ms-body-thingiverse" / "files" / "mini_4wd_ms_chassis.stl") - [4.5, 0, 0]
bx, by, bz = -b[:, 0] * S * sx - 0.15, b[:, 2] * S * sy + 0.4 + lift, b[:, 1] * S * sz
ix, iz = np.floor(bx / CELL).astype(int), np.floor(bz / CELL).astype(int)
top = {}
for i, k, y in zip(ix, iz, by):
    if y > top.get((i, k), -1e9):
        top[(i, k)] = y


def cyl(cx, cy, cz, r, length, axis, n=400):
    t, a = np.random.rand(n) * length - length / 2, np.random.rand(n) * 2 * np.pi
    if axis == "z":
        return np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a), cz + t])
    return np.column_stack([cx + t, cy + r * np.cos(a), cz + r * np.sin(a)])


bracket = super1("-motor-bracket")
mx, my = (bracket[:, 0].min() + bracket[:, 0].max()) / 2, (bracket[:, 1].min() + bracket[:, 1].max()) / 2 + 0.15
ret = super1("-battery-retainer")
gs = 1.0 + (3.7 - 3.5) * 0.22
parts = {
    "Sasis": super1(""),
    "Gear Cover": super1("-gear-cover"),
    "Dudukan Dinamo": bracket,
    "Penutup Saklar": super1("-switch-cover"),
    "Tombol Saklar": super1("-switch-on-off"),
    "Penahan Baterai": ret,
    "Dinamo (kode)": cyl(mx, my, 0, 1.0, 3.6, "z"),
    # Sama dengan index.html untuk sasis model: di antara pinion dan spur as belakang
    "Gear counter (kode)": cyl((mx - 5.4) / 2, (my + R) / 2 + 0.25, 2.35, 0.75 * gs, 0.3, "z"),
    "Gear pinion (kode)": cyl(mx, my, 2.35, 0.45, 0.4, "z"),
    "Baterai (kode)": np.vstack([cyl((ret[:, 0].min() + ret[:, 0].max()) / 2, ret[:, 1].min() - 0.92, z, 0.97, 6.6, "x") for z in (-0.99, 0.99)]),
}
print(f"naik={lift} skala=({sx},{sy},{sz})  body y {by.min():.2f}..{by.max():.2f}")
worst = 0.0
for name, p in parts.items():
    keys = zip(np.floor(p[:, 0] / CELL).astype(int), np.floor(p[:, 2] / CELL).astype(int))
    over = np.array([p[j, 1] - top[k] if k in top else -1e9 for j, k in enumerate(keys)])
    bad = over > -0.08
    worst = max(worst, over.max() + 0.08)
    if bad.any():
        q = p[bad]
        print(f"  MENEMBUS {name:22s} {bad.sum():6d} titik, maks {over.max() + 0.08:5.2f} satuan, "
              f"x {q[:, 0].min():5.1f}..{q[:, 0].max():5.1f}  z {q[:, 2].min():5.1f}..{q[:, 2].max():5.1f}")
print(f"KEKURANGAN TERBESAR {worst:.2f} satuan")
