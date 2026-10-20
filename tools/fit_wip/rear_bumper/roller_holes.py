import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slicer import *
T = np.array([0.977, 13.96, 0.0])
rb = transformed("chassis-super-1-rear-bumper")
ch = transformed("chassis-super-1")
def scan(t, x, y, label, win=5, zs=np.arange(3.0, 22.0, 0.25)):
    sub = t[((np.abs(t[:, :, 0] - x) < win) & (np.abs(t[:, :, 1] - y) < win)).any(1)]
    print(f"== {label} near ({x},{y})")
    prev = None
    for z in zs:
        cs = [(round(a, 3), round(b, 3), round(r, 3)) for a, b, r, e, n in circles(section(sub, "z", z), "z", rmax=8) if np.hypot(a - x, b - y) < 2]
        key = tuple(sorted(set(c[2] for c in cs)))
        if key != prev:
            print(f"   Z>={z:5.2f}: {cs}")
            prev = key
    zz = sub.reshape(-1, 3)
    near = zz[np.hypot(zz[:, 0] - x, zz[:, 1] - y) < 4]
    print(f"   material Z range within r<4: {near[:,2].min():.2f}..{near[:,2].max():.2f}")
for (x, y) in [(14.91, 119.22), (61.17, 119.22), (16.12, 128.06), (59.97, 128.06), (25.40, 128.49), (50.69, 128.49), (25.31, 116.59), (50.78, 116.59), (37.85, 130.32), (25.20, 101.40), (50.88, 101.40)]:
    scan(rb, x, y, "bumper(file coords)")
