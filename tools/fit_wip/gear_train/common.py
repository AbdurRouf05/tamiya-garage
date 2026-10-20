"""Shared helpers: load Super-1 STL triangles (cached as npy), voxelize by Z-ray parity, sim mapping."""
import struct
from pathlib import Path
import numpy as np

WF = Path(r"C:/Users/arack/AppData/Local/Temp/claude/D--coding-cozy-village/bb2493d4-aa52-4045-a5e2-0a655a382ec3/scratchpad/wf/gear_train")
SRC = Path(r"D:/coding/tamiya-garage/models/source/super1-printables")
CACHE = WF / "cache"
S = 0.1346
R = 1.75
NAMES = ["", "-gear-cover", "-motor-bracket", "-rear-bumper", "-switch-cover", "-switch-on-off", "-battery-retainer", "-wheel-bearing"]


def tris(name):
    """(N,3,3) float32 triangles of chassis-super-1{name}.stl"""
    key = name.strip("-") or "chassis"
    c = CACHE / f"{key}.npy"
    if c.exists():
        return np.load(c)
    data = (SRC / f"chassis-super-1{name}.stl").read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    t = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))["v"].copy()
    np.save(c, t)
    return t


def to_sim(p):
    p = np.asarray(p, float)
    X, Y, Z = p[..., 0], p[..., 1], p[..., 2]
    return np.stack([-(Y - 70) * S, (Z - 15.1) * S + R, -(X - 39) * S], -1)


def from_sim(q):
    q = np.asarray(q, float)
    x, y, z = q[..., 0], q[..., 1], q[..., 2]
    return np.stack([39 - z / S, 70 - x / S, 15.1 + (y - R) / S], -1)


class Grid:
    def __init__(self, lo=(0, 0, 0), hi=(80, 125, 36), h=0.2):
        self.lo = np.array(lo, float); self.h = h
        self.n = np.ceil((np.array(hi, float) - self.lo) / h).astype(int)

    def centers(self, ax):
        return self.lo[ax] + (np.arange(self.n[ax]) + 0.5) * self.h


def voxelize(t, g, jitter=(1.234e-4, 2.345e-4)):
    """Occupancy (nx,ny,nz) bool via +Z ray parity at column centres. Returns occ, n_odd_columns."""
    t = t.astype(np.float64)
    a, b, c = t[:, 0], t[:, 1], t[:, 2]
    # 2D area (signed)
    d = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1])
    keep = np.abs(d) > 1e-12
    a, b, c, d = a[keep], b[keep], c[keep], d[keep]
    ox, oy = g.lo[0] + 0.5 * g.h + jitter[0], g.lo[1] + 0.5 * g.h + jitter[1]
    mnx = np.ceil((np.minimum(np.minimum(a[:, 0], b[:, 0]), c[:, 0]) - ox) / g.h).astype(np.int64)
    mxx = np.floor((np.maximum(np.maximum(a[:, 0], b[:, 0]), c[:, 0]) - ox) / g.h).astype(np.int64)
    mny = np.ceil((np.minimum(np.minimum(a[:, 1], b[:, 1]), c[:, 1]) - oy) / g.h).astype(np.int64)
    mxy = np.floor((np.maximum(np.maximum(a[:, 1], b[:, 1]), c[:, 1]) - oy) / g.h).astype(np.int64)
    wx, wy = mxx - mnx + 1, mxy - mny + 1
    ok = (wx > 0) & (wy > 0)
    a, b, c, d, mnx, mny, wx, wy = a[ok], b[ok], c[ok], d[ok], mnx[ok], mny[ok], wx[ok], wy[ok]
    cnt = wx * wy
    cols, zs = [], []
    CH = 2_000_000
    order = np.arange(len(cnt))
    start = 0
    cum = np.cumsum(cnt)
    while start < len(cnt):
        base = cum[start - 1] if start else 0
        end = np.searchsorted(cum, base + CH, side="right")
        end = max(end, start + 1)
        sl = slice(start, end)
        k = cnt[sl]
        tid = np.repeat(np.arange(start, end), k)
        off = np.arange(k.sum()) - np.repeat(np.cumsum(k) - k, k)
        ix = mnx[tid] + off % wx[tid]
        iy = mny[tid] + off // wx[tid]
        px, py = ox + ix * g.h, oy + iy * g.h
        A, B, C, D = a[tid], b[tid], c[tid], d[tid]
        w0 = ((B[:, 0] - px) * (C[:, 1] - py) - (C[:, 0] - px) * (B[:, 1] - py)) / D
        w1 = ((C[:, 0] - px) * (A[:, 1] - py) - (A[:, 0] - px) * (C[:, 1] - py)) / D
        w2 = 1 - w0 - w1
        ins = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        z = w0 * A[:, 2] + w1 * B[:, 2] + w2 * C[:, 2]
        m = ins & (ix >= 0) & (ix < g.n[0]) & (iy >= 0) & (iy < g.n[1])
        cols.append(ix[m] * g.n[1] + iy[m]); zs.append(z[m])
        start = end
    cols = np.concatenate(cols); zs = np.concatenate(zs)
    o = np.lexsort((zs, cols))
    cols, zs = cols[o], zs[o]
    # parity per column
    uc, first, counts = np.unique(cols, return_index=True, return_counts=True)
    odd = counts % 2 == 1
    rank = np.arange(len(cols)) - np.repeat(first, counts)
    good = ~np.repeat(odd, counts)
    enter = good & (rank % 2 == 0)
    leave = good & (rank % 2 == 1)
    k0 = np.clip(np.round((zs[enter] - g.lo[2]) / g.h).astype(np.int64), 0, g.n[2])
    k1 = np.clip(np.round((zs[leave] - g.lo[2]) / g.h).astype(np.int64), 0, g.n[2])
    cc = cols[enter]
    diff = np.zeros((g.n[0] * g.n[1], g.n[2] + 1), np.int16)
    np.add.at(diff, (cc, k0), 1)
    np.add.at(diff, (cc, k1), -1)
    occ = np.cumsum(diff, axis=1)[:, :-1] > 0
    return occ.reshape(g.n[0], g.n[1], g.n[2]), int(odd.sum())
