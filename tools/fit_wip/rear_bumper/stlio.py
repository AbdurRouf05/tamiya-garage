import struct
from pathlib import Path
import numpy as np
SRC = Path(__file__).resolve().parents[3] / "models" / "source" / "super1-printables"
CACHE = Path(__file__).resolve().parent / "cache"
CACHE.mkdir(exist_ok=True)

def tris(name):
    c = CACHE / f"{name}.npy"
    if c.exists():
        return np.load(c)
    data = (SRC / f"{name}.stl").read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    assert len(data) == 84 + n * 50, "not binary"
    t = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    v = t["v"].astype(np.float32).copy()
    np.save(c, v)
    return v

def verts(name):
    c = CACHE / f"{name}_uv.npy"
    if c.exists():
        return np.load(c)
    v = np.unique(tris(name).reshape(-1, 3).round(3), axis=0)
    np.save(c, v)
    return v
