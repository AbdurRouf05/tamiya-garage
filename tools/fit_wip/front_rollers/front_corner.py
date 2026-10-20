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
# restrict to front-left & front-right corners
c = T.mean(1)
for side, (x0, x1) in (("L", (-1, 14)), ("R", (64, 79))):
    sel = T[(c[:, 0] > x0) & (c[:, 0] < x1) & (c[:, 1] < 16)]
    V = sel.reshape(-1, 3)
    print(side, "corner verts bbox", V.min(0).round(2), V.max(0).round(2))
    zs = np.arange(6.0, 14.5, 0.5)
    fig, axs = plt.subplots(3, 6, figsize=(24, 13))
    for ax, z in zip(axs.flat, zs):
        sg = slice_tris(sel, 2, z)
        if len(sg):
            ax.add_collection(LineCollection(sg[:, :, :2], lw=0.8, color="k"))
        ax.set_xlim(x0, x1); ax.set_ylim(-1, 15); ax.set_aspect("equal"); ax.grid(True, lw=0.3)
        ax.set_xticks(range(int(x0), int(x1) + 1, 1)); ax.set_yticks(range(-1, 16, 1)); ax.tick_params(labelsize=5)
        ax.set_title(f"{side} Z={z}")
    # Y-slices through the corner (vertical profile)
    for ax, y in zip(axs.flat[len(zs):], (4.5,)):
        sg = slice_tris(sel, 1, y)
        if len(sg):
            ax.add_collection(LineCollection(sg[:, :, [0, 2]], lw=0.8, color="b"))
        ax.set_xlim(x0, x1); ax.set_ylim(3, 20); ax.set_aspect("equal"); ax.grid(True, lw=0.3); ax.set_title(f"{side} Y={y} (X,Z)")
    plt.tight_layout(); plt.savefig(OUT + f"chassis_front_corner_{side}.png", dpi=70)
