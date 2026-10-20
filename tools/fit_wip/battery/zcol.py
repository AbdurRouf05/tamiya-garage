"""Helpers over rasterized z-columns."""
import numpy as np
import stlcore


class ZCol:
    def __init__(self, tag):
        d = np.load(stlcore.OUT / f"zcol_{tag}.npz")
        self.xs, self.ys, iv = d["xs"], d["ys"], d["iv"]
        self.nx, self.ny = len(self.xs), len(self.ys)
        self.step = self.xs[1] - self.xs[0]
        self.col = iv[:, 0].astype(int); self.z0 = iv[:, 1]; self.z1 = iv[:, 2]

    def grid(self, vals, fill=np.nan, how="min"):
        g = np.full(self.nx * self.ny, fill)
        if how == "min":
            np.fmin.at(g, self.col, vals)
        else:
            np.fmax.at(g, self.col, vals)
        return g.reshape(self.ny, self.nx)

    def overlap_with(self, lo, hi):
        """lo/hi: (ny,nx) arrays of an object's z-range per column (nan = no object). Returns per-column overlap length."""
        L = lo.ravel()[self.col]; H = hi.ravel()[self.col]
        ov = np.clip(np.minimum(H, self.z1) - np.maximum(L, self.z0), 0, None)
        ov = np.nan_to_num(ov)
        g = np.zeros(self.nx * self.ny); np.add.at(g, self.col, ov)
        return g.reshape(self.ny, self.nx)


def cylinder_y(zc, cx, cz, r, y0, y1):
    """z-range of a cylinder with axis along Y on zc grid."""
    X, Y = np.meshgrid(zc.xs, zc.ys)
    dx = X - cx
    h = np.sqrt(np.clip(r * r - dx * dx, 0, None))
    m = (np.abs(dx) < r) & (Y >= y0) & (Y <= y1)
    lo = np.where(m, cz - h, np.nan); hi = np.where(m, cz + h, np.nan)
    return lo, hi
