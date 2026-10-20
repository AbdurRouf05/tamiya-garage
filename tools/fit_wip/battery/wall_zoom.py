"""Zoomed sections of the left and right bay walls (looking for clip features)."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import stlcore
T = stlcore.tris("chassis-super-1.stl")
ys = [50.5, 54.0, 57.5, 60.0, 63.0, 66.0, 70.0, 73.0]
fig, axs = plt.subplots(2, len(ys), figsize=(3.0 * len(ys), 8))
for j, y in enumerate(ys):
    s = stlcore.slice_plane(T, 1, y)
    for i, (x0, x1) in enumerate(((18, 27), (51, 60))):
        ax = axs[i, j]
        ax.add_collection(LineCollection(s[:, :, [0, 2]], colors="k", linewidths=0.8))
        ax.set_xlim(x0, x1); ax.set_ylim(7, 20); ax.set_aspect("equal")
        ax.set_xticks(np.arange(x0, x1 + .1, 1)); ax.set_yticks(np.arange(7, 20.1, 1))
        ax.set_xticks(np.arange(x0, x1 + .1, 0.25), minor=True); ax.set_yticks(np.arange(7, 20.1, 0.25), minor=True)
        ax.grid(True, which="major", lw=0.5, color="b", alpha=0.5); ax.grid(True, which="minor", lw=0.2, color="c", alpha=0.6)
        ax.tick_params(labelsize=6); ax.set_title(f"Y={y} {'left' if i == 0 else 'right'} wall", fontsize=8)
plt.tight_layout()
out = stlcore.OUT / "wall_zoom_y.png"
plt.savefig(out, dpi=100); print(out)
# longitudinal along wall
fig, axs = plt.subplots(4, 1, figsize=(16, 11))
for ax, x in zip(axs, (21.5, 22.5, 55.5, 56.5)):
    s = stlcore.slice_plane(T, 0, x)
    ax.add_collection(LineCollection(s[:, :, 1:], colors="k", linewidths=0.7))
    ax.set_xlim(30, 95); ax.set_ylim(6, 20); ax.set_aspect("equal")
    ax.set_xticks(np.arange(30, 96, 5)); ax.set_xticks(np.arange(30, 96, 1), minor=True)
    ax.set_yticks(np.arange(6, 20.1, 2)); ax.set_yticks(np.arange(6, 20.1, 0.5), minor=True)
    ax.grid(True, which="major", lw=0.5, color="b", alpha=0.5); ax.grid(True, which="minor", lw=0.2, color="c", alpha=0.6)
    ax.tick_params(labelsize=7); ax.set_title(f"X={x} (Y horiz, Z up)", fontsize=9)
plt.tight_layout()
out = stlcore.OUT / "wall_zoom_x.png"
plt.savefig(out, dpi=100); print(out)
