"""Shared helpers (read-only access to project files)."""
import struct
from pathlib import Path

import numpy as np

PROJ = Path(r"D:\coding\tamiya-garage")
SRC = PROJ / "models" / "source" / "super1-printables"
OUT = Path(__file__).resolve().parent
CACHE = OUT / "cache"
CACHE.mkdir(exist_ok=True)
S = 0.1346
R = 1.75


def stl_tris(path):
    path = Path(path)
    c = CACHE / (path.stem + "_tris.npy")
    if c.exists():
        return np.load(c)
    data = path.read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    tri = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    t = np.ascontiguousarray(tri["v"])
    np.save(c, t)
    return t


def part(name):
    """Triangles (N,3,3) of chassis-super-1<name>.stl in STL mm."""
    return stl_tris(SRC / f"chassis-super-1{name}.stl")


def mm_to_sim(p):
    p = np.asarray(p, dtype=np.float64)
    x = -(p[..., 1] - 70) * S
    y = (p[..., 2] - 15.1) * S + R
    z = -(p[..., 0] - 39) * S
    return np.stack([x, y, z], axis=-1)


def sim_to_mm(q):
    q = np.asarray(q, dtype=np.float64)
    Y = 70 - q[..., 0] / S
    Z = (q[..., 1] - R) / S + 15.1
    X = 39 - q[..., 2] / S
    return np.stack([X, Y, Z], axis=-1)


PARTS = {"chassis": "", "gear_cover": "-gear-cover", "motor_bracket": "-motor-bracket", "rear_bumper": "-rear-bumper",
         "switch_cover": "-switch-cover", "switch_knob": "-switch-on-off", "battery_retainer": "-battery-retainer",
         "wheel_bearing": "-wheel-bearing"}
