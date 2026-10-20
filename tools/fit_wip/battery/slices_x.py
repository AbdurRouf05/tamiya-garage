"""Longitudinal sections (X=const, YZ plane) of chassis bay; optional battery rectangles."""
import sys, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import stlcore
T = stlcore.tris("chassis-super-1.stl")
xs = [float(a) for a in sys.argv[1].split(",")]
bat = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else None  # {"cx":[..],"cz":..,"r":..,"y0":..,"y1":..}
tag = sys.argv[3] if len(sys.argv) > 3 else ""
fig, axs = plt.subplots(len(xs), 1, figsize=(16, 3.3 * len(xs)))
axs = np.atleast_1d(axs)
for ax, x in zip(axs, xs):
    seg = stlcore.slice_plane(T, 0, x)
    ax.add_collection(LineCollection(seg[:, :, 1:], colors="k", linewidths=0.6))
    if bat:
        for cx in bat["cx"]:
            dx = x - cx
            if abs(dx) < bat["r"]:
                h = np.sqrt(bat["r"] ** 2 - dx ** 2)
                ax.add_patch(plt.Rectangle((bat["y0"], bat["cz"] - h), bat["y1"] - bat["y0"], 2 * h, fill=False, color="r", lw=1))
    ax.set_xlim(20, 100); ax.set_ylim(3, 21); ax.set_aspect("equal")
    ax.set_xticks(np.arange(20, 101, 5)); ax.set_yticks(np.arange(3, 22, 2))
    ax.set_xticks(np.arange(20, 101, 1), minor=True); ax.set_yticks(np.arange(3, 22, 0.5), minor=True)
    ax.grid(True, which="major", lw=0.6, color="b", alpha=0.5); ax.grid(True, which="minor", lw=0.2, color="c", alpha=0.6)
    ax.set_title(f"X={x} (Y horiz: front=left, Z up)"); ax.tick_params(labelsize=7)
plt.tight_layout()
out = stlcore.OUT / f"bay_x{tag}_{xs[0]}-{xs[-1]}.png"
plt.savefig(out, dpi=95); print(out)
