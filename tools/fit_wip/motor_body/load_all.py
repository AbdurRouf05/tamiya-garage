import numpy as np
from common import *
for k, n in PARTS.items():
    t = part(n)
    v = t.reshape(-1, 3)
    print(f"{k:18s} tris={len(t):9d} min={v.min(0).round(2)} max={v.max(0).round(2)}")
