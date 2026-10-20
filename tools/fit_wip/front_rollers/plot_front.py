"""Top & side sections of the front end (STL mm): chassis, tyres, Magnum/Sayap body, current sim rollers/plate, roller candidates."""
from scene_parts import *
from stlslice import slice_tris
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, Rectangle, Polygon

ch = tris("chassis-super-1.stl")
c = ch.mean(1)
chF = ch[c[:, 1] < 45]
sw = tris("chassis-super-1-switch-cover.stl")
bodies = {"Magnum": sample_surface(magnum_tris(), 300), "Sayap S1": sample_surface(sayap_tris(), 300)}
holes = [(2.005, 6.262), (4.474, 3.115), (76.024, 6.262), (73.555, 3.115)]
cur_rollers = to_stl(np.array([[9.32, 2.10, 4.80], [9.32, 2.10, -4.80]]))
cur_plate = to_stl(np.array([[8.67, 1.85, 5.40], [10.27, 1.99, -5.40]]))
tyre_x = [(39 - W / S) - TW / S / 2, (39 - W / S) + TW / S / 2]

fig, axs = plt.subplots(2, 2, figsize=(22, 15))
for col, (bn, P) in enumerate(bodies.items()):
    Q = to_stl(P)
    ax = axs[0, col]
    # chassis outline at Z=10 and 13
    for z, colr in ((10.0, "0.4"), (13.2, "k")):
        sg = slice_tris(chF, 2, z)
        ax.add_collection(LineCollection(sg[:, :, :2], lw=0.7, color=colr))
    sg = slice_tris(sw, 2, 13.5)
    if len(sg):
        ax.add_collection(LineCollection(sg[:, :, :2], lw=0.7, color="m"))
    band = Q[(Q[:, 2] > 13.0) & (Q[:, 2] < 21.0) & (Q[:, 1] < 30)]
    ax.scatter(band[:, 0], band[:, 1], s=0.3, c=band[:, 2], cmap="viridis", vmin=11, vmax=21)
    for x0 in tyre_x:
        ax.add_patch(Rectangle((x0 - 0.0, 17.0), 0, 0))
    for xc in (39 - W / S, 39 + W / S):
        ax.add_patch(Rectangle((xc - TW / S / 2, 30 - TR / S), TW / S, 2 * TR / S, fill=False, ec="k", lw=1.2, ls="--"))
    for (hx, hy) in holes:
        ax.add_patch(Circle((hx, hy), 1.0, fill=False, ec="r", lw=1))
        ax.add_patch(Circle((hx, hy), 6.5, fill=False, ec="r", lw=0.8, ls=":"))
        ax.add_patch(Circle((hx, hy), 0.65 / S, fill=False, ec="orange", lw=0.8, ls="-."))
    for r in cur_rollers:
        ax.add_patch(Circle((r[0], r[1]), 0.65 / S, fill=False, ec="b", lw=1.5))
        ax.plot(r[0], r[1], "b+")
    ax.add_patch(Rectangle((cur_plate[:, 0].min(), cur_plate[:, 1].min()), np.ptp(cur_plate[:, 0]), np.ptp(cur_plate[:, 1]), fill=False, ec="c", lw=1.5))
    ax.set_xlim(-12, 90); ax.set_ylim(-10, 46); ax.set_aspect("equal"); ax.grid(True, lw=0.3)
    ax.set_xticks(range(-10, 91, 5)); ax.set_yticks(range(-10, 46, 5))
    ax.set_title(f"TOP (X right, Y up = toward rear). black: chassis @Z13.2, grey @Z10, magenta: switch cover(file pos)@Z13.5,\n"
                 f"dots: {bn} body surface Z13..21 (colour=Z), dashed: tyres, red: holes + true 13mm roller, orange: sim r0.65 roller at hole,\nblue: CURRENT sim roller, cyan: CURRENT sim FRP plate", fontsize=8)
    # side view: section at X = hole A left (X 2.0) and band of X
    ax = axs[1, col]
    for xs, colr in ((2.0, "k"), (4.5, "0.5")):
        sg = slice_tris(chF, 0, xs)
        if len(sg):
            ax.add_collection(LineCollection(sg[:, :, 1:], lw=0.8, color=colr))
    sel = Q[(np.abs(Q[:, 0] - 3.2) < 4.0) & (Q[:, 1] < 30)]
    ax.scatter(sel[:, 1], sel[:, 2], s=0.3, c="g")
    t = np.linspace(0, 2 * np.pi, 100)
    ax.plot(30 + TR / S * np.cos(t), 15.1 + TR / S * np.sin(t), "k--", lw=1)
    for (hx, hy), zb in (((2.005, 6.262), 13.70), ((4.474, 3.115), 13.32)):
        ax.add_patch(Rectangle((hy - 6.5, zb), 13, 0.72 / S, fill=False, ec="r", ls=":"))
        ax.add_patch(Rectangle((hy - 0.65 / S, zb), 2 * 0.65 / S, 0.72 / S, fill=False, ec="orange", ls="-."))
    r = cur_rollers[0]
    ax.add_patch(Rectangle((r[1] - 0.65 / S, r[2] - 0.36 / S), 2 * 0.65 / S, 0.72 / S, fill=False, ec="b", lw=1.5))
    ax.add_patch(Rectangle((cur_plate[:, 1].min(), cur_plate[:, 2].min()), np.ptp(cur_plate[:, 1]), np.ptp(cur_plate[:, 2]), fill=False, ec="c", lw=1.5))
    ax.axhline(15.1 - TR / S, color="brown", lw=1)
    ax.set_xlim(-10, 46); ax.set_ylim(0, 30); ax.set_aspect("equal"); ax.grid(True, lw=0.3)
    ax.set_xticks(range(-10, 46, 2)); ax.set_yticks(range(0, 31, 2))
    ax.set_title(f"SIDE section (Y right = toward rear, Z up). chassis sections X=2.0 (black) / 4.5 (grey); green: {bn} body pts with |X-3.2|<4;\n"
                 "red dotted: true 13mm roller on boss at hole A/B; orange: sim-size roller; blue: CURRENT sim roller; cyan: CURRENT plate; brown: ground", fontsize=8)
plt.tight_layout()
plt.savefig(HERE / "front_top_side_before.png", dpi=75)
print("ok")
