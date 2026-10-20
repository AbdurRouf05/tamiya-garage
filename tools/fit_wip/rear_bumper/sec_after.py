"""python sec_after.py axis value u0 u1 v0 v1 ppm tag  (bumper translated by corrected transform)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slicer import *
W = os.path.dirname(os.path.abspath(__file__))
T = np.array([0.977, 13.96, 0.0])
ax, val = sys.argv[1], float(sys.argv[2]); u0, u1, v0, v1, ppm = (float(v) for v in sys.argv[3:8]); tag = sys.argv[8]
ch = transformed("chassis-super-1"); rb = transformed("chassis-super-1-rear-bumper") + T
ch = ch[(ch[:, :, 1] > 60).any(1)]
s1 = section(ch, ax, val); s2 = section(rb, ax, val)
marks = [(42.3895, 111.835, 1.25, (0, 0, 255))] if ax == "z" else []
draw([(s1, (80, 80, 80)), (s2, (230, 100, 0))], ax, val, ((u0, u1), (v0, v1)), ppm, os.path.join(W, "renders", f"after_sec{ax.upper()}_{val:05.2f}_{tag}.png"), marks=marks, title="AFTER: gray=chassis orange=rear-bumper moved (+0.977,+13.96,0)")
