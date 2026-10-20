"""Ray-parity voxelisation of a (watertight) triangle soup on a fixed global grid."""
import numpy as np

def voxelize(t, origin, h, shape):
    """t: (n,3,3) triangles. origin: grid corner; voxel (i,j,k) centre = origin + (idx+0.5)*h. returns bool array shape."""
    nx, ny, nz = shape
    ox, oy, oz = origin
    p0, p1, p2 = t[:, 0, :2], t[:, 1, :2], t[:, 2, :2]
    mn = np.minimum(np.minimum(p0, p1), p2); mx = np.maximum(np.maximum(p0, p1), p2)
    i0 = np.ceil((mn[:, 0] - ox) / h - 0.5).astype(np.int64); i1 = np.floor((mx[:, 0] - ox) / h - 0.5).astype(np.int64)
    j0 = np.ceil((mn[:, 1] - oy) / h - 0.5).astype(np.int64); j1 = np.floor((mx[:, 1] - oy) / h - 0.5).astype(np.int64)
    i0 = np.clip(i0, 0, nx); i1 = np.clip(i1, -1, nx - 1); j0 = np.clip(j0, 0, ny); j1 = np.clip(j1, -1, ny - 1)
    ni = np.maximum(i1 - i0 + 1, 0); nj = np.maximum(j1 - j0 + 1, 0)
    cnt = ni * nj
    sel = np.nonzero(cnt)[0]
    tri = np.repeat(sel, cnt[sel])
    start = np.repeat(np.cumsum(cnt[sel]) - cnt[sel], cnt[sel])
    local = np.arange(len(tri)) - start
    ii = i0[tri] + local // nj[tri]; jj = j0[tri] + local % nj[tri]
    px = ox + (ii + 0.5) * h; py = oy + (jj + 0.5) * h
    a, b, c = t[tri, 0], t[tri, 1], t[tri, 2]
    v0x, v0y = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
    v1x, v1y = c[:, 0] - a[:, 0], c[:, 1] - a[:, 1]
    v2x, v2y = px - a[:, 0], py - a[:, 1]
    den = v0x * v1y - v1x * v0y
    ok = np.abs(den) > 1e-14
    den = np.where(ok, den, 1)
    u = (v2x * v1y - v1x * v2y) / den
    v = (v0x * v2y - v2x * v0y) / den
    inside = ok & (u >= 0) & (v >= 0) & (u + v < 1)
    # half-open rule handled approximately by grid jitter (origin chosen off-lattice)
    z = a[:, 2] + u * (b[:, 2] - a[:, 2]) + v * (c[:, 2] - a[:, 2])
    ii, jj, z = ii[inside], jj[inside], z[inside]
    kk = np.ceil((z - oz) / h - 0.5).astype(np.int64)   # first voxel centre above the hit
    kk = np.clip(kk, 0, nz)
    tog = np.zeros((nx, ny, nz + 1), np.int32)
    np.add.at(tog, (ii, jj, kk), 1)
    occ = (np.cumsum(tog, axis=2)[:, :, :nz] % 2).astype(bool)
    return occ
