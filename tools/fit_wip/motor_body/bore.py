import numpy as np
from common import *
from slicer import *
br = part("-motor-bracket")
# refine axis: fit circle to hood inner arc at X=44 (points with r in 9.8..10.2 about guess)
cy, cz = 86.35, 17.75
for it in range(3):
    pts = []
    for X in np.arange(34, 55, 1.0):
        s = slice_tris(br, 0, X).reshape(-1, 3)
        r = np.hypot(s[:, 1] - cy, s[:, 2] - cz)
        pts.append(s[np.abs(r - 10) < 0.3])
    p = np.concatenate(pts)[:, 1:]
    A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]
    b = (p ** 2).sum(1)
    sol = np.linalg.lstsq(A, b, rcond=None)[0]
    cy, cz = sol[0], sol[1]; rr = np.sqrt(sol[2] + cy ** 2 + cz ** 2)
    print(f"hood fit: centre Y={cy:.3f} Z={cz:.3f} r={rr:.3f} n={len(p)} resid={np.std(np.hypot(p[:,0]-cy,p[:,1]-cz)-rr):.3f}")
# small holes: fit circles to the r~3.2 holes at X=30 and X=58
for X0 in (29.0, 29.5, 30.0, 30.5, 31.0, 56.0, 56.5, 57.0, 57.5, 58.0, 58.5):
    s = slice_tris(br, 0, X0).reshape(-1, 3)[:, 1:]
    r = np.hypot(s[:, 0] - cy, s[:, 1] - cz)
    for lo_, hi_ in ((2.5, 4.0), (4.5, 6)):
        q = s[(r > lo_) & (r < hi_)]
        if len(q) > 10:
            A = np.c_[2 * q[:, 0], 2 * q[:, 1], np.ones(len(q))]; b = (q ** 2).sum(1)
            so = np.linalg.lstsq(A, b, rcond=None)[0]
            print(f"  X={X0}: circle r~{lo_}-{hi_}: centre Y={so[0]:.3f} Z={so[1]:.3f} r={np.sqrt(so[2]+so[0]**2+so[1]**2):.3f} (n={len(q)})")
print("radial min clearance along X (sectors: top=+Z, front=-Y, bottom=-Z, back=+Y)")
for X in np.arange(22.0, 59.5, 0.5):
    s = slice_tris(br, 0, X).reshape(-1, 3)
    if not len(s):
        print(f"X={X:5.1f}: none"); continue
    dy, dz = s[:, 1] - cy, s[:, 2] - cz
    r = np.hypot(dy, dz); a = np.degrees(np.arctan2(dz, dy))
    sec = {"top": (a > 45) & (a < 135), "front": (a > 135) | (a < -135), "bottom": (a < -45) & (a > -135), "back": (a > -45) & (a < 45)}
    print(f"X={X:5.1f}: rmin all {r.min():5.2f} | " + " ".join(f"{k} {r[m].min() if m.any() else np.nan:5.2f}" for k, m in sec.items()))
