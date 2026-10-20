"""Heightmaps of the chassis bay: bottom Z, floor-top Z (top of lowest solid), and through-holes."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import stlcore
from zcol import ZCol
zc = ZCol("chassis")
bottom = zc.grid(zc.z0, how="min")
# floor top: top of lowest interval per column
o = np.lexsort((zc.z0, zc.col)); first = np.r_[True, zc.col[o][1:] != zc.col[o][:-1]]
ft = np.full(zc.nx * zc.ny, np.nan); ft[zc.col[o][first]] = zc.z1[o][first]; ft = ft.reshape(zc.ny, zc.nx)
top = zc.grid(zc.z1, how="max")
ext = [zc.xs[0], zc.xs[-1], zc.ys[0], zc.ys[-1]]
fig, axs = plt.subplots(1, 3, figsize=(20, 11))
for ax, g, t, cm, vr in ((axs[0], bottom, "bottom Z (lowest solid)", "viridis", (4, 9)), (axs[1], ft, "top of lowest solid layer (floor top)", "turbo", (5, 15)), (axs[2], top, "highest solid Z", "turbo", (5, 20))):
    im = ax.imshow(g, origin="lower", extent=ext, cmap=cm, vmin=vr[0], vmax=vr[1], interpolation="nearest")
    plt.colorbar(im, ax=ax, fraction=0.04)
    ax.set_title(t + " ; white = no material (through-hole)")
    ax.set_xticks(np.arange(14, 65, 2)); ax.set_yticks(np.arange(28, 101, 2)); ax.tick_params(labelsize=6)
    ax.grid(True, lw=0.3, color="k", alpha=0.3)
    ax.set_facecolor("white")
plt.tight_layout(); out = stlcore.OUT / "bay_heightmaps.png"; plt.savefig(out, dpi=90); print(out)
np.save(stlcore.OUT / "cache" / "floortop.npy", ft)
# statistics in battery footprint region
X, Y = np.meshgrid(zc.xs, zc.ys)
for (xa, xb) in ((25.5, 39.4), (40.7, 54.7)):
    m = (X > xa) & (X < xb) & (Y > 37.5) & (Y < 88)
    print(f"X {xa}..{xb}: bottom min {np.nanmin(bottom[m]):.3f}, floor-top values (rounded) :", np.unique(np.round(ft[m][~np.isnan(ft[m])], 2), return_counts=True))
print("overall chassis bottom in bay window X20..58 Y36..93:", np.nanmin(bottom[(X > 20) & (X < 58) & (Y > 36) & (Y < 93)]))
