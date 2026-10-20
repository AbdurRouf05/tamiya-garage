"""Shared helpers: load binary STL to numpy triangle array (cached), plane slicing, ray columns."""
import struct
from pathlib import Path

import numpy as np

SRC = Path(r"D:\coding\tamiya-garage\models\source\super1-printables")
OUT = Path(r"C:\Users\arack\AppData\Local\Temp\claude\D--coding-cozy-village\bb2493d4-aa52-4045-a5e2-0a655a382ec3\scratchpad\wf\battery")
CACHE = OUT / "cache"
CACHE.mkdir(exist_ok=True)


def tris(name):
    """Return (n,3,3) float32 triangle vertices for STL file name (in SRC)."""
    c = CACHE / (name + ".npy")
    if c.exists():
        return np.load(c)
    data = (SRC / name).read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    assert len(data) == 84 + n * 50, "not binary STL"
    t = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    v = np.ascontiguousarray(t["v"])
    np.save(c, v)
    return v


def slice_plane(T, axis, val):
    """Intersect triangles with plane coord[axis]=val. Returns (m,2,3) segments."""
    d = T[:, :, axis] - val
    s = np.sign(d)
    s[s == 0] = 1e-9
    cross = (s.min(1) < 0) & (s.max(1) > 0)
    Tc, dc = T[cross], d[cross]
    segs = []
    pts_all = []
    for (i, j) in ((0, 1), (1, 2), (2, 0)):
        di, dj = dc[:, i], dc[:, j]
        m = (di * dj) < 0
        t = np.where(m, di / np.where(m, di - dj, 1), 0)
        p = Tc[:, i] + (Tc[:, j] - Tc[:, i]) * t[:, None]
        pts_all.append((m, p))
    # each crossing triangle has exactly 2 crossing edges (ignoring degenerate)
    ms = np.stack([m for m, _ in pts_all], 1)
    ps = np.stack([p for _, p in pts_all], 1)
    good = ms.sum(1) == 2
    ms, ps = ms[good], ps[good]
    idx = np.argsort(~ms, axis=1, kind="stable")[:, :2]
    seg = np.take_along_axis(ps, idx[:, :, None], 1)
    return seg


def ray_hits(T, axis, a_val, b_val):
    """Intersections of a line parallel to `axis` passing through the other two coords (a_val, b_val).
    Returns sorted coordinate values along `axis` and normal sign of the hit triangle (+1 facing +axis)."""
    others = [k for k in range(3) if k != axis]
    A = T[:, :, others[0]] - a_val
    B = T[:, :, others[1]] - b_val
    # bbox prefilter
    m = (A.min(1) <= 0) & (A.max(1) >= 0) & (B.min(1) <= 0) & (B.max(1) >= 0)
    Tm = T[m]
    A, B = A[m], B[m]
    # barycentric in 2D
    x0, y0 = A[:, 0], B[:, 0]
    x1, y1 = A[:, 1], B[:, 1]
    x2, y2 = A[:, 2], B[:, 2]
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    ok = np.abs(den) > 1e-12
    l0 = ((y1 - y2) * (0 - x2) + (x2 - x1) * (0 - y2)) / np.where(ok, den, 1)
    l1 = ((y2 - y0) * (0 - x2) + (x0 - x2) * (0 - y2)) / np.where(ok, den, 1)
    l2 = 1 - l0 - l1
    inside = ok & (l0 >= -1e-7) & (l1 >= -1e-7) & (l2 >= -1e-7)
    vals = (l0 * Tm[:, 0, axis] + l1 * Tm[:, 1, axis] + l2 * Tm[:, 2, axis])[inside]
    Ti = Tm[inside]
    n = np.cross(Ti[:, 1] - Ti[:, 0], Ti[:, 2] - Ti[:, 0])[:, axis]
    o = np.argsort(vals)
    return vals[o], np.sign(n[o])


def column_intervals(T, axis, a_val, b_val, tol=1e-4):
    """Solid intervals along a ray (pairs of entry/exit), merging duplicate hits."""
    v, s = ray_hits(T, axis, a_val, b_val)
    if len(v) == 0:
        return []
    # merge near-duplicate hits (shared edges)
    keep = np.ones(len(v), bool)
    for i in range(1, len(v)):
        if abs(v[i] - v[i - 1]) < tol and s[i] == s[i - 1]:
            keep[i] = False
    v, s = v[keep], s[keep]
    out = []
    depth = 0
    start = None
    for val, sg in zip(v, s):
        if sg < 0:  # entering (normal points against +axis)
            if depth == 0:
                start = val
            depth += 1
        else:
            depth -= 1
            if depth == 0 and start is not None:
                out.append((round(float(start), 3), round(float(val), 3)))
            depth = max(depth, 0)
    return out
