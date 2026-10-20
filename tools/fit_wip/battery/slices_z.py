"""Horizontal (Z=const) cross-sections of the Super-1 chassis, plotted with mm grid."""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

import stlcore

T = stlcore.tris("chassis-super-1.stl")
R = stlcore.tris("chassis-super-1-battery-retainer.stl")
zs = [float(a) for a in sys.argv[1:]] or [4.5, 5.5, 6.5, 8, 10, 12, 14, 16, 18]
fig, axs = plt.subplots(1, len(zs), figsize=(4.2 * len(zs), 7))
for ax, z in zip(np.atleast_1d(axs), zs):
    seg = stlcore.slice_plane(T, 2, z)
    ax.add_collection(LineCollection(seg[:, :, :2], colors="k", linewidths=0.4))
    rs = stlcore.slice_plane(R, 2, z)
    if len(rs):
        ax.add_collection(LineCollection(rs[:, :, :2], colors="r", linewidths=0.6))
    ax.set_xlim(-2, 80)
    ax.set_ylim(-2, 124)
    ax.set_aspect("equal")
    ax.set_xticks(np.arange(0, 81, 10))
    ax.set_yticks(np.arange(0, 125, 10))
    ax.set_xticks(np.arange(0, 81, 2), minor=True)
    ax.set_yticks(np.arange(0, 125, 2), minor=True)
    ax.grid(True, which="major", lw=0.5, color="b", alpha=0.5)
    ax.grid(True, which="minor", lw=0.2, color="c", alpha=0.4)
    ax.set_title(f"Z={z}")
    ax.tick_params(labelsize=6)
plt.tight_layout()
out = stlcore.OUT / ("slices_z_" + "_".join(str(z) for z in zs) + ".png")
plt.savefig(out, dpi=110)
print(out)
