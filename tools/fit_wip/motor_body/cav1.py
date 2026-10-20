import numpy as np, matplotlib.pyplot as plt
from common import *
from slicer import *
br = part("-motor-bracket"); ch = part("")
lo, hi = np.array([10, 65, 0]), np.array([70, 115, 35])
ch = ch[np.all((ch.max(1) >= lo) & (ch.min(1) <= hi), axis=1)]
fig, axs = plt.subplots(2, 3, figsize=(21, 14))
for ax, X in zip(axs.flat, [25, 30, 36, 44, 50, 57]):
    plot_slices(ax, [(ch, "k", 0.8), (br, "r", 0.8)], 0, X, 1, 2)
    ax.set_title(f"X={X} YZ plane (h=Y, v=Z)"); ax.set_xlim(72, 112); ax.set_ylim(2, 34)
    ax.set_xticks(range(72, 113, 2)); ax.set_yticks(range(2, 35, 2)); ax.tick_params(labelsize=7)
    ax.add_patch(plt.Circle((86.35, 17.75), 10.05, fill=False, color="b", lw=0.5, ls="--"))
fig.tight_layout(); fig.savefig("cav_YZ.png", dpi=75)
# radial profile around a guessed axis from slices
for X in (36, 44, 50):
    s = slice_tris(br, 0, X).reshape(-1, 3)
    for cy, cz in ((86.35, 17.75),):
        d = np.hypot(s[:, 1] - cy, s[:, 2] - cz); a = np.degrees(np.arctan2(s[:, 2] - cz, s[:, 1] - cy))
        print("X", X)
        for a0 in range(-180, 180, 15):
            m = (a >= a0) & (a < a0 + 15)
            print(f"   ang {a0:4d}..{a0+15:4d}: min r {d[m].min() if m.any() else np.nan:6.2f}")
