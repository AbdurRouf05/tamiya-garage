import sys
sys.path.insert(0, r"C:/Users/arack/AppData/Local/Temp/claude/D--coding-cozy-village/bb2493d4-aa52-4045-a5e2-0a655a382ec3/scratchpad/wf/front_rollers")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from stlslice import tris, slice_tris
OUT = r"C:/Users/arack/AppData/Local/Temp/claude/D--coding-cozy-village/bb2493d4-aa52-4045-a5e2-0a655a382ec3/scratchpad/wf/front_rollers/"
T = tris("chassis-super-1.stl")
V = T.reshape(-1, 3)
print("chassis bbox", V.min(0).round(2), V.max(0).round(2), "tris", len(T))
# Z-distribution of vertices in front region
front = V[V[:, 1] < 30]
print("front region bbox", front.min(0).round(2), front.max(0).round(2))
zs = [4.5, 5.5, 6.5, 8, 10, 12, 14, 16, 18, 19]
fig, axs = plt.subplots(2, 5, figsize=(30, 14))
for ax, z in zip(axs.flat, zs):
    sg = slice_tris(T, 2, z)
    ax.add_collection(LineCollection(sg[:, :, :2], lw=0.6, color="k"))
    ax.set_xlim(-2, 80); ax.set_ylim(-2, 45); ax.set_aspect("equal"); ax.grid(True, lw=0.3)
    ax.set_xticks(range(0, 81, 5)); ax.set_yticks(range(0, 46, 5)); ax.tick_params(labelsize=6)
    ax.set_title(f"Z={z} mm (front region, X horiz, Y vert)")
plt.tight_layout(); plt.savefig(OUT + "chassis_front_zslices.png", dpi=80)
print("saved")
