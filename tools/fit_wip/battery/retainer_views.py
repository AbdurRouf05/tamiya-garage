"""Sections of retainer (red) over chassis (black), with optional retainer offset dX,dY,dZ."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import stlcore
T = stlcore.tris("chassis-super-1.stl")
R = stlcore.tris("chassis-super-1-battery-retainer.stl").copy()
off = np.array([float(a) for a in sys.argv[1].split(",")]) if len(sys.argv) > 1 else np.zeros(3)
tag = sys.argv[2] if len(sys.argv) > 2 else "file"
R += off
views = [("y", 51.0), ("y", 54.0), ("y", 57.0), ("z", 14.5), ("z", 16.5), ("z", 18.5), ("x", 22.0), ("x", 56.0)]
fig, axs = plt.subplots(len(views) // 2, 2, figsize=(15, 4.0 * len(views) // 2))
for ax, (ax_name, val) in zip(axs.ravel(), views):
    k = "xyz".index(ax_name)
    keep = [i for i in range(3) if i != k]
    for M, c, lw in ((T, "k", 0.6), (R, "r", 0.9)):
        s = stlcore.slice_plane(M, k, val)
        if len(s):
            ax.add_collection(LineCollection(s[:, :, keep], colors=c, linewidths=lw))
    if ax_name == "y":
        ax.set_xlim(16, 62); ax.set_ylim(4, 21)
    elif ax_name == "z":
        ax.set_xlim(16, 62); ax.set_ylim(44, 64)
    else:
        ax.set_xlim(40, 70); ax.set_ylim(4, 21)
    xl, yl = ax.get_xlim(), ax.get_ylim()
    ax.set_xticks(np.arange(xl[0], xl[1] + .1, 2)); ax.set_yticks(np.arange(yl[0], yl[1] + .1, 1))
    ax.set_xticks(np.arange(xl[0], xl[1] + .1, 0.5), minor=True); ax.set_yticks(np.arange(yl[0], yl[1] + .1, 0.5), minor=True)
    ax.grid(True, which="major", lw=0.5, color="b", alpha=0.5); ax.grid(True, which="minor", lw=0.2, color="c", alpha=0.6)
    ax.set_aspect("equal"); ax.tick_params(labelsize=6)
    lab = {"y": "X horiz, Z up", "z": "X horiz, Y up", "x": "Y horiz, Z up"}[ax_name]
    ax.set_title(f"{ax_name.upper()}={val}  ({lab})  retainer offset {tuple(off)}", fontsize=9)
plt.tight_layout()
out = stlcore.OUT / f"retainer_{tag}.png"
plt.savefig(out, dpi=100); print(out)
