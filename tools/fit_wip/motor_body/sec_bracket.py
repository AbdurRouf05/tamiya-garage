import numpy as np, matplotlib.pyplot as plt
from common import *
from slicer import *
P = {k: part(v) for k, v in PARTS.items() if k in ("chassis", "motor_bracket", "gear_cover", "rear_bumper")}
def crop(t, lo, hi):
    v = t
    m = np.all((v.max(1) >= lo) & (v.min(1) <= hi), axis=1)
    return t[m]
lo, hi = np.array([10, 70, 0]), np.array([70, 125, 35])
P = {k: crop(v, lo, hi) for k, v in P.items()}
col = {"chassis": "k", "motor_bracket": "r", "gear_cover": "b", "rear_bumper": "g"}
# YZ sections at several X
fig, axs = plt.subplots(3, 3, figsize=(18, 16))
for ax, X in zip(axs.flat, [20, 24, 28, 32, 39, 46, 52, 56, 58]):
    plot_slices(ax, [(P[k], col[k], 0.6) for k in P], 0, X, 1, 2)
    ax.set_title(f"X={X} (YZ plane; h=Y, v=Z)")
    ax.set_xlim(70, 125); ax.set_ylim(0, 35)
fig.tight_layout(); fig.savefig("sec_bracket_YZ.png", dpi=70)
fig, axs = plt.subplots(3, 3, figsize=(18, 14))
for ax, Y in zip(axs.flat, [78, 82, 86, 88, 90, 92, 95, 99, 103]):
    plot_slices(ax, [(P[k], col[k], 0.6) for k in P], 1, Y, 0, 2)
    ax.set_title(f"Y={Y} (XZ plane; h=X, v=Z)")
    ax.set_xlim(10, 70); ax.set_ylim(0, 35)
fig.tight_layout(); fig.savefig("sec_bracket_XZ.png", dpi=70)
fig, axs = plt.subplots(3, 3, figsize=(18, 16))
for ax, Z in zip(axs.flat, [5, 7, 10, 13, 16, 19, 22, 26, 30]):
    plot_slices(ax, [(P[k], col[k], 0.6) for k in P], 2, Z, 0, 1)
    ax.set_title(f"Z={Z} (XY plane; h=X, v=Y)")
    ax.set_xlim(10, 70); ax.set_ylim(70, 125)
fig.tight_layout(); fig.savefig("sec_bracket_XY.png", dpi=70)
