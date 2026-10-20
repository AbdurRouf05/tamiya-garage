"""Shared helpers: binary STL loading and planar slicing (STL mm)."""
import struct
from pathlib import Path
import numpy as np

SRC = Path(r"D:/coding/tamiya-garage/models/source/super1-printables")
S, R = 0.1346, 1.75


def tris(name):
    p = SRC / name if not str(name).startswith(("C:", "D:")) else Path(name)
    data = p.read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    t = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    return t["v"].astype(np.float64)  # (n,3,3)


def slice_tris(T, axis, value):
    """Return segments (m,2,3) where the plane coord[axis]==value cuts triangles."""
    d = T[:, :, axis] - value
    s = np.sign(d)
    cut = (s.max(1) > 0) & (s.min(1) < 0)
    T, d = T[cut], d[cut]
    segs = []
    for tri, dd in zip(T, d):
        pts = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            if (dd[i] > 0) != (dd[j] > 0):
                t = dd[i] / (dd[i] - dd[j])
                pts.append(tri[i] + t * (tri[j] - tri[i]))
        if len(pts) == 2:
            segs.append(pts)
    return np.array(segs)


def to_sim(P, R=R):
    P = np.asarray(P, float)
    return np.column_stack([-(P[..., 1] - 70) * S, (P[..., 2] - 15.1) * S + R, -(P[..., 0] - 39) * S])


def to_stl(Q, R=R):
    Q = np.asarray(Q, float)
    return np.column_stack([39 - Q[..., 2] / S, 70 - Q[..., 0] / S, 15.1 + (Q[..., 1] - R) / S])


def ray_z(T, x, y):
    """All Z where the vertical line (x,y) crosses the mesh (barycentric test in XY)."""
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    m = (np.minimum(np.minimum(a[:, 0], b[:, 0]), c[:, 0]) <= x) & (np.maximum(np.maximum(a[:, 0], b[:, 0]), c[:, 0]) >= x) & \
        (np.minimum(np.minimum(a[:, 1], b[:, 1]), c[:, 1]) <= y) & (np.maximum(np.maximum(a[:, 1], b[:, 1]), c[:, 1]) >= y)
    a, b, c = a[m], b[m], c[m]
    v0, v1 = b[:, :2] - a[:, :2], c[:, :2] - a[:, :2]
    p = np.array([x, y]) - a[:, :2]
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    ok = np.abs(den) > 1e-12
    u = np.where(ok, (p[:, 0] * v1[:, 1] - v1[:, 0] * p[:, 1]) / np.where(ok, den, 1), -1)
    v = np.where(ok, (v0[:, 0] * p[:, 1] - p[:, 0] * v0[:, 1]) / np.where(ok, den, 1), -1)
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1)
    z = a[hit, 2] + u[hit] * (b[hit, 2] - a[hit, 2]) + v[hit] * (c[hit, 2] - a[hit, 2])
    return np.unique(np.round(np.sort(z), 3))


def fit_circle(P):
    A = np.column_stack([2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))])
    bb = (P ** 2).sum(1)
    cx, cy, k = np.linalg.lstsq(A, bb, rcond=None)[0]
    return cx, cy, np.sqrt(k + cx ** 2 + cy ** 2)
