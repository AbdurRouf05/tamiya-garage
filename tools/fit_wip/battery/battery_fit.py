"""Find where AA cylinders (axis along Y) rest in the bay without penetrating the chassis.
For each cx: drop the cylinder from above and find the resting centre height cz (first contact)."""
import numpy as np
import stlcore
from zcol import ZCol
zc = ZCol("chassis")
X = np.repeat(zc.xs[None, :], zc.ny, 0).ravel()
Y = np.repeat(zc.ys[:, None], zc.nx, 1).ravel()
cX, cY = X[zc.col], Y[zc.col]


def rest_cz(cx, r, y0, y1, start=24.0):
    dx = cX - cx
    m = (np.abs(dx) < r) & (cY >= y0) & (cY <= y1)
    h = np.sqrt(r * r - dx[m] ** 2)
    lo, hi = zc.z0[m] - h, zc.z1[m] + h  # forbidden cz ranges
    # descend from start: first contact = max(hi) among those with hi <= start ; ensure start free
    assert not np.any((lo < start) & (hi > start)), "start not free"
    k = hi <= start
    j = np.argmax(np.where(k, hi, -1e9))
    return hi[j], (cX[m][j], cY[m][j], zc.z1[m][j])


def free_y_range(cx, cz, r, ymid=62.7, tol=1e-3):
    """Largest Y window around ymid where the cylinder cross-section (cx,cz,r) hits nothing."""
    dx = cX - cx
    m = np.abs(dx) < r
    h = np.sqrt(r * r - dx[m] ** 2)
    ov = (np.minimum(cz + h, zc.z1[m]) - np.maximum(cz - h, zc.z0[m])) > tol
    yb = cY[m][ov]
    front = yb[yb < ymid].max() if np.any(yb < ymid) else None
    back = yb[yb > ymid].min() if np.any(yb > ymid) else None
    return front, back


if __name__ == "__main__":
    Y0, Y1 = 37.465, 87.965
    for r in (7.0, 7.25):
        print(f"=== r={r} (dia {2*r}) Y {Y0}..{Y1} ===")
        for side, rng in (("left", np.arange(29.5, 36.01, 0.05)), ("right", np.arange(44.0, 48.51, 0.05))):
            res = [(cx, *rest_cz(cx, r, Y0, Y1)) for cx in rng]
            best = min(res, key=lambda t: t[1])
            print(f"{side}: lowest rest cz={best[1]:.3f} at cx={best[0]:.3f} (contact col x={best[2][0]:.2f} y={best[2][1]:.2f} solid top z={best[2][2]:.3f}); bottom z={best[1]-r:.3f}")
            for cx, cz, c in res[:: 10]:
                print(f"   cx={cx:.2f} cz={cz:.3f} contact at x={c[0]:.2f}, y={c[1]:.2f}")
