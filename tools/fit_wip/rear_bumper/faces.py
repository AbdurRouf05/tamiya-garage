"""List horizontal (+/-Z) and vertical (+/-Y, +/-X) planar face levels with area inside a box."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slicer import transformed
import numpy as np
def planes(name, box, axis, T=(0,0,0), tol_n=0.999):
    t = transformed(name) + np.array(T)
    c = t.mean(1)
    m = np.all((c >= box[0]) & (c <= box[1]), axis=1)
    t = t[m]
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]); a = np.linalg.norm(n, axis=1) / 2
    nn = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    out = {}
    for sgn in (1, -1):
        k = nn[:, axis] * sgn > tol_n
        lv = np.round(t[k][:, 0, axis], 2)
        for L in np.unique(lv):
            out[(sgn, L)] = a[k][lv == L].sum()
    return out
if __name__ == "__main__":
    name = sys.argv[1]; axis = "xyz".index(sys.argv[2])
    box = np.array([[float(v) for v in sys.argv[3:6]], [float(v) for v in sys.argv[6:9]]])
    T = [float(v) for v in sys.argv[9:12]] if len(sys.argv) > 9 else (0, 0, 0)
    for (s, L), A in sorted(planes(name, box, axis, T).items(), key=lambda kv: kv[0][1]):
        if A > 0.3: print(f"  normal {'+' if s>0 else '-'}{sys.argv[2]}  level {L:8.2f}  area {A:8.2f} mm2")
