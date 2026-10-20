import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slicer import *
ch = transformed("chassis-super-1"); rb = transformed("chassis-super-1-rear-bumper")
def fit_near(t, x, y, zs, r_expect, win=3.0):
    res = []
    sub = t[((np.abs(t[:, :, 0] - x) < win) & (np.abs(t[:, :, 1] - y) < win)).any(1)]
    for z in zs:
        s = section(sub, "z", z)
        for cx, cy, r, e, n in circles(s, "z"):
            if abs(r - r_expect) < 0.2 and np.hypot(cx - x, cy - y) < 1:
                res.append((z, cx, cy, r, e, n))
    return res
for nm, t, x, y, zs, r in [("chassis floor hole", ch, 42.39, 111.84, np.arange(5.4, 6.8, 0.1), 1.25),
                           ("bumper tab hole", rb, 41.41, 97.87, np.arange(6.8, 8.3, 0.1), 1.25)]:
    R = np.array([q[:4] for q in fit_near(t, x, y, zs, r)])
    print(nm, "n=", len(R), "Z", R[:, 0].min().round(2), "..", R[:, 0].max().round(2), "centre", R[:, 1].mean().round(4), R[:, 2].mean().round(4), "std", R[:, 1].std().round(4), R[:, 2].std().round(4), "r", R[:, 3].mean().round(3))
# chassis boss underneath: what is the r2.77 thing at Z 5.3-5.9
for z in np.arange(5.3, 6.0, 0.1):
    sub = ch[((np.abs(ch[:, :, 0] - 42.4) < 5) & (np.abs(ch[:, :, 1] - 111.8) < 5)).any(1)]
    print("chassis Z=%.2f" % z, [(round(a, 3), round(b, 3), round(r, 3)) for a, b, r, e, n in circles(section(sub, "z", z), "z")])
