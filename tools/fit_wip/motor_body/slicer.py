import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


def slice_tris(t, axis, c):
    """Segments (M,2,3) where plane coord[axis]==c cuts triangles t (N,3,3)."""
    d = t[:, :, axis] - c
    mn, mx = d.min(1), d.max(1)
    sel = (mn < 0) & (mx > 0)
    t, d = t[sel].astype(np.float64), d[sel].astype(np.float64)
    segs = []
    pts = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        di, dj = d[:, i], d[:, j]
        cross = (di * dj) < 0
        w = np.where(cross, di / np.where(cross, di - dj, 1), 0)
        p = t[:, i] + (t[:, j] - t[:, i]) * w[:, None]
        pts.append((cross, p))
    out = []
    # each triangle crossing has exactly 2 crossing edges (ignoring exact-vertex hits)
    cr = np.stack([p[0] for p in pts], 1)
    P = np.stack([p[1] for p in pts], 1)
    ok = cr.sum(1) == 2
    cr, P = cr[ok], P[ok]
    idx = np.argsort(~cr, axis=1, kind="stable")[:, :2]
    a = P[np.arange(len(P)), idx[:, 0]]
    b = P[np.arange(len(P)), idx[:, 1]]
    return np.stack([a, b], 1)


def plot_slices(ax, items, axis, c, h_axis, v_axis):
    for t, color, lw in items:
        s = slice_tris(t, axis, c)
        if len(s):
            ax.add_collection(LineCollection(s[:, :, [h_axis, v_axis]], colors=color, linewidths=lw))
    ax.set_aspect("equal")
    ax.autoscale()
    ax.grid(True, lw=0.3)
