"""Fit circles to the battery cradle arcs in the chassis (sections Y=const through the cradle ribs)."""
import numpy as np
import stlcore
T = stlcore.tris("chassis-super-1.stl")

def fit_circle(p):
    A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]
    b = (p ** 2).sum(1)
    cx, cz, c = np.linalg.lstsq(A, b, rcond=None)[0]
    r = np.sqrt(c + cx ** 2 + cz ** 2)
    res = np.hypot(p[:, 0] - cx, p[:, 1] - cz) - r
    return cx, cz, r, np.abs(res).max()

for y in (52.6, 53.0, 54.0, 55.0, 55.8, 67.8, 68.5, 70.0, 71.0, 71.4):
    s = stlcore.slice_plane(T, 1, y)
    p = s.reshape(-1, 3)[:, [0, 2]]
    p = np.unique(p.round(4), axis=0)
    out = []
    for lo, hi in ((24.0, 39.0), (39.0, 55.5)):
        # arc points: inside the bay, above floor top+0.05, below Z 13.5, not on straight lines
        m = (p[:, 0] > lo) & (p[:, 0] < hi) & (p[:, 1] > 6.9) & (p[:, 1] < 13.3)
        q = p[m]
        if len(q) < 8:
            out.append("n/a"); continue
        # keep points that are on a curve: iterative fit with outlier rejection
        for _ in range(4):
            cx, cz, r, e = fit_circle(q)
            d = np.abs(np.hypot(q[:, 0] - cx, q[:, 1] - cz) - r)
            q = q[d < max(0.05, np.percentile(d, 80))]
        cx, cz, r, e = fit_circle(q)
        out.append(f"cx={cx:.3f} cz={cz:.3f} r={r:.3f} (bottom z={cz - r:.3f}, n={len(q)}, maxres={e:.3f}, x {q[:,0].min():.2f}..{q[:,0].max():.2f}, z..{q[:,1].max():.2f})")
    print(f"Y={y}: L {out[0]}\n        R {out[1]}")
