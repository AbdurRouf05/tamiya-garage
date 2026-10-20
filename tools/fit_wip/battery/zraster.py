"""Rasterize a triangle mesh into Z-columns on a regular XY grid -> list of solid intervals per column.
Saves npz with grid definition and a ragged interval table (col index, z0, z1)."""
import sys
import numpy as np
import stlcore


def zcolumns(T, x0, x1, y0, y1, step, off=0.0137):
    xs = np.arange(x0, x1 + 1e-9, step) + off
    ys = np.arange(y0, y1 + 1e-9, step) + off
    nx, ny = len(xs), len(ys)
    sel = (T[:, :, 0].max(1) >= xs[0]) & (T[:, :, 0].min(1) <= xs[-1]) & (T[:, :, 1].max(1) >= ys[0]) & (T[:, :, 1].min(1) <= ys[-1])
    T = T[sel].astype(np.float64)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])[:, 2]
    T = T[np.abs(n) > 1e-12]; n = n[np.abs(n) > 1e-12]
    ix0 = np.clip(np.ceil((T[:, :, 0].min(1) - xs[0]) / step).astype(int), 0, nx - 1)
    ix1 = np.clip(np.floor((T[:, :, 0].max(1) - xs[0]) / step).astype(int), 0, nx - 1)
    iy0 = np.clip(np.ceil((T[:, :, 1].min(1) - ys[0]) / step).astype(int), 0, ny - 1)
    iy1 = np.clip(np.floor((T[:, :, 1].max(1) - ys[0]) / step).astype(int), 0, ny - 1)
    cx = np.maximum(ix1 - ix0 + 1, 0); cy = np.maximum(iy1 - iy0 + 1, 0)
    ok = (cx > 0) & (cy > 0)
    T, n, ix0, iy0, cx, cy = T[ok], n[ok], ix0[ok], iy0[ok], cx[ok], cy[ok]
    cols, zs, sg = [], [], []
    CH = 200000
    for s in range(0, len(T), CH):
        t, nn, a0, b0, ca, cb = T[s:s + CH], n[s:s + CH], ix0[s:s + CH], iy0[s:s + CH], cx[s:s + CH], cy[s:s + CH]
        cnt = ca * cb
        tri = np.repeat(np.arange(len(t)), cnt)
        start = np.repeat(np.cumsum(cnt) - cnt, cnt)
        k = np.arange(cnt.sum()) - start
        gi = a0[tri] + k % ca[tri]
        gj = b0[tri] + k // ca[tri]
        px, py = xs[gi], ys[gj]
        tt = t[tri]
        x0_, y0_ = tt[:, 0, 0], tt[:, 0, 1]
        x1_, y1_ = tt[:, 1, 0], tt[:, 1, 1]
        x2_, y2_ = tt[:, 2, 0], tt[:, 2, 1]
        den = (y1_ - y2_) * (x0_ - x2_) + (x2_ - x1_) * (y0_ - y2_)
        l0 = ((y1_ - y2_) * (px - x2_) + (x2_ - x1_) * (py - y2_)) / den
        l1 = ((y2_ - y0_) * (px - x2_) + (x0_ - x2_) * (py - y2_)) / den
        l2 = 1 - l0 - l1
        ins = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
        z = l0 * tt[:, 0, 2] + l1 * tt[:, 1, 2] + l2 * tt[:, 2, 2]
        cols.append((gj * nx + gi)[ins]); zs.append(z[ins]); sg.append(np.sign(nn[tri])[ins])
    cols = np.concatenate(cols); zs = np.concatenate(zs); sg = np.concatenate(sg)
    o = np.lexsort((zs, cols))
    cols, zs, sg = cols[o], zs[o], sg[o]
    # pair: walk with depth counter (python loop over hits, vectorised by column via cumsum of -sign)
    d = np.cumsum(-sg)  # entering (normal down, sign -1) increments
    # reset per column: subtract cumsum at column start
    first = np.r_[True, cols[1:] != cols[:-1]]
    base = np.maximum.accumulate(np.where(first, np.arange(len(cols)), 0))
    dprev = np.where(first, 0, d - (-sg))  # depth before this hit
    dprev = dprev - np.where(first, 0, (d - (-sg))[base] - 0)  # placeholder (recomputed below)
    # simpler exact recompute per column
    depth_before = np.empty(len(cols)); 
    run = 0.0; last = -1
    iv = []
    for i in range(len(cols)):
        c = cols[i]
        if c != last:
            run = 0; last = c
        if sg[i] < 0:
            if run == 0:
                zin = zs[i]
            run += 1
        else:
            if run > 0:
                run -= 1
                if run == 0:
                    iv.append((c, zin, zs[i]))
    iv = np.array(iv)
    return xs, ys, iv


if __name__ == "__main__":
    name, tag = sys.argv[1], sys.argv[2]
    x0, x1, y0, y1, step = map(float, sys.argv[3:8])
    T = stlcore.tris(name)
    xs, ys, iv = zcolumns(T, x0, x1, y0, y1, step)
    np.savez(stlcore.OUT / f"zcol_{tag}.npz", xs=xs, ys=ys, iv=iv)
    print(tag, len(xs), len(ys), len(iv), "intervals")
