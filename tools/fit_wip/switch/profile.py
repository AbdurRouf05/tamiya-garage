import numpy as np, sys
from vox import Grid
g = Grid([14, -1, 3], [64, 36, 24], 0.1)
z = np.load("cache/vox_file.npz")
X = g.centers(0); Y = g.centers(1); Z = g.centers(2)
def runs(mask, coords):
    """return list of (start,end) of True runs"""
    m = np.concatenate([[False], mask, [False]]).astype(int)
    d = np.diff(m); s = np.nonzero(d == 1)[0]; e = np.nonzero(d == -1)[0]
    return [(round(coords[a] - g.h / 2, 2), round(coords[b - 1] + g.h / 2, 2)) for a, b in zip(s, e)]
def ix(ax, v): return int(round((v - g.lo[ax]) / g.h))
name = sys.argv[1]; V = z[name]
mode = sys.argv[2]
if mode == "zcol":  # Z runs at given (x,y)
    for xy in sys.argv[3:]:
        x, y = map(float, xy.split(","))
        print(f"{name} x={x} y={y} Z-runs:", runs(V[ix(0, x), ix(1, y)], Z))
elif mode == "ycol":  # Y runs at (x,z)
    for xz in sys.argv[3:]:
        x, zz = map(float, xz.split(","))
        print(f"{name} x={x} z={zz} Y-runs:", runs(V[ix(0, x), :, ix(2, zz)], Y))
elif mode == "xcol":
    for yz in sys.argv[3:]:
        y, zz = map(float, yz.split(","))
        print(f"{name} y={y} z={zz} X-runs:", runs(V[:, ix(1, y), ix(2, zz)], X))
