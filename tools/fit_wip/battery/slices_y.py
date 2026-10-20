"""Transverse sections (Y=const, XZ plane) of the chassis around the battery bay; optional battery circles."""
import sys, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import stlcore
T = stlcore.tris("chassis-super-1.stl")
ys = [float(a) for a in sys.argv[1].split(",")]
bat = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None   # {"cx":[..], "cz":.., "r":..}
tag = sys.argv[3] if len(sys.argv) > 3 else ""
n = len(ys); cols = min(n, 4); rows = (n + cols - 1) // cols
fig, axs = plt.subplots(rows, cols, figsize=(6.2 * cols, 3.6 * rows))
axs = np.atleast_1d(axs).ravel()
for ax, y in zip(axs, ys):
    seg = stlcore.slice_plane(T, 1, y)
    ax.add_collection(LineCollection(seg[:, :, [0, 2]], colors="k", linewidths=0.7))
    if bat:
        for cx in bat["cx"]:
            ax.add_patch(plt.Circle((cx, bat["cz"]), bat["r"], fill=False, color="r", lw=1))
    ax.set_xlim(14, 64); ax.set_ylim(3, 21); ax.set_aspect("equal")
    ax.set_xticks(np.arange(14, 65, 5)); ax.set_yticks(np.arange(3, 22, 2))
    ax.set_xticks(np.arange(14, 65, 1), minor=True); ax.set_yticks(np.arange(3, 22, 0.5), minor=True)
    ax.grid(True, which="major", lw=0.6, color="b", alpha=0.5); ax.grid(True, which="minor", lw=0.2, color="c", alpha=0.6)
    ax.set_title(f"Y={y} (X horiz, Z up)"); ax.tick_params(labelsize=7)
for ax in axs[n:]:
    ax.axis("off")
plt.tight_layout()
out = stlcore.OUT / f"bay_y{tag}_{ys[0]}-{ys[-1]}.png"
plt.savefig(out, dpi=100); print(out)
