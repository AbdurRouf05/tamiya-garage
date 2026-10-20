import sys; sys.path.insert(0, r"C:/Users/arack/AppData/Local/Temp/claude/D--coding-cozy-village/bb2493d4-aa52-4045-a5e2-0a655a382ec3/scratchpad/wf/rear_bumper")
from stlio import *
for n in ["chassis-super-1", "chassis-super-1-rear-bumper"]:
    t = tris(n); v = t.reshape(-1,3)
    print(n, len(t), "min", v.min(0).round(2), "max", v.max(0).round(2))
    verts(n)
