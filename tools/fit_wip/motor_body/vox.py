"""Solid voxelization of closed triangle meshes by ray parity along axis 2 (Z), plus surface voxelization.

Grid: voxel (i,j,k) centre = origin + (i+0.5, j+0.5, k+0.5) * h.
"""
import numpy as np

EPS = np.array([0.01371, 0.00917])  # sub-voxel jitter (in voxel units) so rays avoid mesh edges/vertices


class Grid:
    def __init__(self, lo, hi, h):
        self.h = float(h)
        self.lo = np.asarray(lo, dtype=np.float64)
        self.shape = tuple(int(np.ceil(v)) for v in (np.asarray(hi) - self.lo) / self.h)

    def centers(self, axis):
        return self.lo[axis] + (np.arange(self.shape[axis]) + 0.5) * self.h

    def to_index(self, p):
        return np.floor((np.asarray(p) - self.lo) / self.h).astype(np.int64)


def solid(tris, g, chunk=400000, return_odd=False):
    """tris (N,3,3) float -> bool occupancy (shape g.shape). Columns with odd crossing counts are dropped."""
    nx, ny, nz = g.shape
    cols, zs = [], []
    T = (np.asarray(tris, dtype=np.float64) - g.lo) / g.h  # voxel units
    for s in range(0, len(T), chunk):
        t = T[s:s + chunk]
        a, b, c = t[:, 0], t[:, 1], t[:, 2]
        # 2D signed area
        det = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1])
        ok = np.abs(det) > 1e-12
        a, b, c, det = a[ok], b[ok], c[ok], det[ok]
        xmin = np.minimum(np.minimum(a[:, 0], b[:, 0]), c[:, 0]); xmax = np.maximum(np.maximum(a[:, 0], b[:, 0]), c[:, 0])
        ymin = np.minimum(np.minimum(a[:, 1], b[:, 1]), c[:, 1]); ymax = np.maximum(np.maximum(a[:, 1], b[:, 1]), c[:, 1])
        i0 = np.ceil(xmin - 0.5 - EPS[0]).astype(np.int64); i1 = np.floor(xmax - 0.5 - EPS[0]).astype(np.int64)
        j0 = np.ceil(ymin - 0.5 - EPS[1]).astype(np.int64); j1 = np.floor(ymax - 0.5 - EPS[1]).astype(np.int64)
        wi, wj = i1 - i0 + 1, j1 - j0 + 1
        has = (wi > 0) & (wj > 0)
        a, b, c, det, i0, j0, wi, wj = a[has], b[has], c[has], det[has], i0[has], j0[has], wi[has], wj[has]
        small = (wi <= 6) & (wj <= 6)
        groups = [(np.where(small)[0], 6, 6)]
        big = np.where(~small)[0]
        for idx in groups:
            pass
        def emit(sel, ii, jj):
            px = ii + 0.5 + EPS[0]; py = jj + 0.5 + EPS[1]
            A, B, C, D = a[sel], b[sel], c[sel], det[sel]
            w0 = ((B[:, 0] - px) * (C[:, 1] - py) - (C[:, 0] - px) * (B[:, 1] - py)) / D
            w1 = ((C[:, 0] - px) * (A[:, 1] - py) - (A[:, 0] - px) * (C[:, 1] - py)) / D
            w2 = 1 - w0 - w1
            inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
            z = w0 * A[:, 2] + w1 * B[:, 2] + w2 * C[:, 2]
            ii, jj, z = ii[inside], jj[inside], z[inside]
            inb = (ii >= 0) & (ii < nx) & (jj >= 0) & (jj < ny)
            cols.append(ii[inb] * ny + jj[inb]); zs.append(z[inb])
        sm = np.where(small)[0]
        for di in range(6):
            for dj in range(6):
                sel = sm[(wi[sm] > di) & (wj[sm] > dj)]
                if len(sel):
                    emit(sel, i0[sel] + di, j0[sel] + dj)
        for k in big:
            ii, jj = np.meshgrid(np.arange(i0[k], i0[k] + wi[k]), np.arange(j0[k], j0[k] + wj[k]), indexing="ij")
            ii, jj = ii.ravel(), jj.ravel()
            emit(np.full(len(ii), k), ii, jj)
    col = np.concatenate(cols); z = np.concatenate(zs)
    order = np.lexsort((z, col)); col, z = col[order], z[order]
    uc, start, cnt = np.unique(col, return_index=True, return_counts=True)
    odd = cnt % 2 == 1
    keep = np.repeat(~odd, cnt)
    col, z = col[keep], z[keep]
    # pair consecutive entries within each column
    zin, zout, cc = z[0::2], z[1::2], col[0::2]
    k0 = np.clip(np.ceil(zin - 0.5).astype(np.int64), 0, nz)
    k1 = np.clip(np.floor(zout - 0.5).astype(np.int64) + 1, 0, nz)
    good = k1 > k0
    k0, k1, cc = k0[good], k1[good], cc[good]
    diff = np.zeros((nx * ny, nz + 1), dtype=np.int16)
    np.add.at(diff, (cc, k0), 1)
    np.add.at(diff, (cc, k1), -1)
    occ = np.cumsum(diff[:, :nz], axis=1, dtype=np.int16) > 0
    occ = occ.reshape(nx, ny, nz)
    if return_odd:
        return occ, int(odd.sum()), len(uc)
    return occ


def surface(tris, g, step=0.4):
    """Mark voxels touched by triangle surfaces (dense barycentric sampling, spacing <= step voxels)."""
    T = (np.asarray(tris, dtype=np.float64) - g.lo) / g.h
    occ = np.zeros(g.shape, dtype=bool)
    e = np.maximum(np.linalg.norm(T[:, 1] - T[:, 0], axis=1), np.maximum(np.linalg.norm(T[:, 2] - T[:, 1], axis=1), np.linalg.norm(T[:, 0] - T[:, 2], axis=1)))
    n = np.maximum(1, np.ceil(e / step).astype(np.int64))
    for nn in np.unique(n):
        sel = np.where(n == nn)[0]
        u, v = np.meshgrid(np.arange(nn + 1), np.arange(nn + 1), indexing="ij")
        m = u + v <= nn
        u, v = u[m] / nn, v[m] / nn
        for s in range(0, len(sel), max(1, 2000000 // len(u))):
            t = T[sel[s:s + max(1, 2000000 // len(u))]]
            p = t[:, None, 0] + u[None, :, None] * (t[:, None, 1] - t[:, None, 0]) + v[None, :, None] * (t[:, None, 2] - t[:, None, 0])
            idx = np.floor(p.reshape(-1, 3)).astype(np.int64)
            ok = np.all((idx >= 0) & (idx < np.array(g.shape)), axis=1)
            idx = idx[ok]
            occ[idx[:, 0], idx[:, 1], idx[:, 2]] = True
    return occ
