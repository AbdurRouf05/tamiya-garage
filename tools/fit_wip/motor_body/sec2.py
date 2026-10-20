import numpy as np, matplotlib.pyplot as plt
from common import *
from slicer import *
br = part("-motor-bracket"); ch = part("")
lo, hi = np.array([10, 65, 0]), np.array([70, 115, 35])
ch = ch[np.all((ch.max(1) >= lo) & (ch.min(1) <= hi), axis=1)]
fig, axs = plt.subplots(2, 4, figsize=(28, 16))
for ax, Z in zip(axs.flat, [4.5, 5.6, 6.2, 7.5, 9.0, 11.0, 13.0, 14.5]):
    plot_slices(ax, [(ch, "k", 0.8), (br, "r", 1.0)], 2, Z, 0, 1)
    ax.set_title(f"Z={Z} XY (h=X, v=Y)"); ax.set_xlim(14, 64); ax.set_ylim(70, 112)
    ax.set_xticks(range(14, 65, 2)); ax.set_yticks(range(70, 113, 2)); ax.tick_params(labelsize=6)
fig.tight_layout(); fig.savefig("sec2_XY.png", dpi=60)
