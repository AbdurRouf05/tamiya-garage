from scene_parts import *
from stlslice import slice_tris
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
rb = tris("chassis-super-1-rear-bumper.stl")
ch = tris("chassis-super-1.stl")
c = ch.mean(1)
chR = ch[c[:, 1] > 80]
V = rb.reshape(-1, 3)
print("rear bumper bbox", V.min(0).round(3), V.max(0).round(3), "tris", len(rb))
print("chassis rear region bbox", chR.reshape(-1, 3).min(0).round(3), chR.reshape(-1, 3).max(0).round(3))
zs = [5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5]
fig, axs = plt.subplots(4, 4, figsize=(28, 30))
for ax, z in zip(axs.flat, zs):
    sg = slice_tris(chR, 2, z)
    if len(sg): ax.add_collection(LineCollection(sg[:, :, :2], lw=0.5, color="0.6"))
    sg = slice_tris(rb, 2, z)
    if len(sg): ax.add_collection(LineCollection(sg[:, :, :2], lw=0.8, color="r"))
    ax.set_xlim(5, 72); ax.set_ylim(85, 138); ax.set_aspect("equal"); ax.grid(True, lw=0.3)
    ax.set_xticks(range(5, 73, 5)); ax.set_yticks(range(85, 139, 5)); ax.tick_params(labelsize=6)
    ax.set_title(f"Z={z}: red rear-bumper (file pos), grey chassis")
plt.tight_layout(); plt.savefig(HERE / "rear_bumper_zslices.png", dpi=55)
