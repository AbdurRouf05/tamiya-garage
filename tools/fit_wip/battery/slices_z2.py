"""Zoomed horizontal sections of the battery-bay region (one PNG per Z)."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import stlcore
T = stlcore.tris("chassis-super-1.stl")
R = stlcore.tris("chassis-super-1-battery-retainer.stl")
xl = (10, 68); yl = (22, 96)
zs = [float(a) for a in sys.argv[1:]]
fig, axs = plt.subplots(1, len(zs), figsize=(6.5 * len(zs), 8.5))
for ax, z in zip(np.atleast_1d(axs), zs):
    seg = stlcore.slice_plane(T, 2, z)
    ax.add_collection(LineCollection(seg[:, :, :2], colors="k", linewidths=0.6))
    rs = stlcore.slice_plane(R, 2, z)
    if len(rs):
        ax.add_collection(LineCollection(rs[:, :, :2], colors="r", linewidths=0.8))
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect("equal")
    ax.set_xticks(np.arange(xl[0], xl[1] + 1, 5)); ax.set_yticks(np.arange(yl[0], yl[1] + 1, 5))
    ax.set_xticks(np.arange(xl[0], xl[1] + 1, 1), minor=True); ax.set_yticks(np.arange(yl[0], yl[1] + 1, 1), minor=True)
    ax.grid(True, which="major", lw=0.6, color="b", alpha=0.5); ax.grid(True, which="minor", lw=0.25, color="c", alpha=0.5)
    ax.set_title(f"chassis section Z={z} mm (red = retainer file pos)"); ax.tick_params(labelsize=7)
plt.tight_layout()
out = stlcore.OUT / ("bay_z_" + "_".join(str(z) for z in zs) + ".png")
plt.savefig(out, dpi=100); print(out)
