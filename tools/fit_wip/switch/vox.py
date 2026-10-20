import numpy as np
OFF = 0.0123457
class Grid:
    def __init__(self, lo, hi, h):
        self.lo = np.array(lo, float) + OFF; self.h = h
        self.n = np.ceil((np.array(hi, float) - self.lo) / h).astype(int) + 1
    def centers(self, ax):
        return self.lo[ax] + np.arange(self.n[ax]) * self.h

def voxelize(t, g, M=None):
    """t: (N,3,3) triangles; M: optional 4x4 transform. returns bool (nx,ny,nz)."""
    t = t.astype(np.float64)
    if M is not None:
        M = np.asarray(M, float)
        t = t @ M[:3, :3].T + M[:3, 3]
    nx, ny, nz = g.n
    h = g.h
    # keep triangles overlapping grid XY
    mn = t[:, :, :2].min(1); mx = t[:, :, :2].max(1)
    hiXY = g.lo[:2] + (g.n[:2] - 1) * h
    keep = (mx[:, 0] >= g.lo[0]) & (mn[:, 0] <= hiXY[0]) & (mx[:, 1] >= g.lo[1]) & (mn[:, 1] <= hiXY[1])
    t = t[keep]
    a, b, c = t[:, 0], t[:, 1], t[:, 2]
    d = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    ok = np.abs(d) > 1e-12
    t, a, b, c, d = t[ok], a[ok], b[ok], c[ok], d[ok]
    i0 = np.ceil((t[:, :, 0].min(1) - g.lo[0]) / h).astype(int)
    i1 = np.floor((t[:, :, 0].max(1) - g.lo[0]) / h).astype(int)
    j0 = np.ceil((t[:, :, 1].min(1) - g.lo[1]) / h).astype(int)
    j1 = np.floor((t[:, :, 1].max(1) - g.lo[1]) / h).astype(int)
    i0 = np.clip(i0, 0, nx); j0 = np.clip(j0, 0, ny); i1 = np.clip(i1, -1, nx - 1); j1 = np.clip(j1, -1, ny - 1)
    W = np.zeros((nx, ny, nz + 1), np.int16)
    sx = i1 - i0 + 1; sy = j1 - j0 + 1
    has = (sx > 0) & (sy > 0)
    def emit(idx, I, J):
        px = g.lo[0] + I * h; py = g.lo[1] + J * h
        A, B, C, D = a[idx], b[idx], c[idx], d[idx]
        wa = ((B[:, 0] - px) * (C[:, 1] - py) - (B[:, 1] - py) * (C[:, 0] - px)) / D
        wb = ((C[:, 0] - px) * (A[:, 1] - py) - (C[:, 1] - py) * (A[:, 0] - px)) / D
        wc = 1 - wa - wb
        inside = (wa >= 0) & (wb >= 0) & (wc >= 0)
        z = wa * A[:, 2] + wb * B[:, 2] + wc * C[:, 2]
        k = np.floor((z - g.lo[2]) / h).astype(int) + 1
        k = np.clip(k, 0, nz)
        dw = -np.sign(D).astype(np.int16)
        m = inside
        np.add.at(W, (I[m], J[m], k[m]), dw[m])
    small = has & (sx <= 6) & (sy <= 6)
    sidx = np.nonzero(small)[0]
    for di in range(6):
        for dj in range(6):
            sel = sidx[(sx[sidx] > di) & (sy[sidx] > dj)]
            if len(sel):
                emit(sel, i0[sel] + di, j0[sel] + dj)
    for ti in np.nonzero(has & ~small)[0]:
        I, J = np.meshgrid(np.arange(i0[ti], i1[ti] + 1), np.arange(j0[ti], j1[ti] + 1), indexing='ij')
        I = I.ravel(); J = J.ravel()
        emit(np.full(len(I), ti), I, J)
    inside = np.cumsum(W, axis=2)[:, :, :nz] > 0
    return inside

def T(dx=0, dy=0, dz=0):
    M = np.eye(4); M[:3, 3] = [dx, dy, dz]; return M
