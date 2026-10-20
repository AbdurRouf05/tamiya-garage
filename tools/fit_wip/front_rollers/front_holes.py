import sys
sys.path.insert(0, r"C:/Users/arack/AppData/Local/Temp/claude/D--coding-cozy-village/bb2493d4-aa52-4045-a5e2-0a655a382ec3/scratchpad/wf/front_rollers")
import numpy as np
from stlslice import tris, slice_tris, ray_z, fit_circle, to_sim
T = tris("chassis-super-1.stl")
c = T.mean(1)
corner = T[(c[:, 1] < 16) & ((c[:, 0] < 14) | (c[:, 0] > 64))]
holes = {}
for z in (9.0, 10.0, 11.0, 12.0):
    sg = slice_tris(corner, 2, z)
    P = sg.reshape(-1, 3)[:, :2]
    for name, guess in (("L_A", (2.0, 6.3)), ("L_B", (4.5, 3.1)), ("R_A", (76.0, 6.3)), ("R_B", (73.5, 3.1))):
        d = np.hypot(P[:, 0] - guess[0], P[:, 1] - guess[1])
        Q = P[d < 1.6]
        cx, cy, r = fit_circle(Q)
        holes.setdefault(name, []).append((cx, cy, r))
        print(f"Z={z} {name}: centre ({cx:.3f},{cy:.3f}) dia {2*r:.3f} n={len(Q)}")
print()
for name, L in holes.items():
    a = np.array(L).mean(0)
    zs = ray_z(T, a[0], a[1])
    sim = to_sim(np.array([[a[0], a[1], 13.3]]))[0]
    print(f"{name}: mean centre X={a[0]:.3f} Y={a[1]:.3f} dia={2*a[2]:.3f}  ray hits Z={zs}  sim x={sim[0]:.3f} z={sim[2]:.3f}")
# lobe outline (outer) at Z=11: fit outer arcs
sg = slice_tris(corner, 2, 11.0)
P = sg.reshape(-1, 3)[:, :2]
for name, h in (("L_A", holes["L_A"][2]), ("L_B", holes["L_B"][2])):
    d = np.hypot(P[:, 0] - h[0], P[:, 1] - h[1])
    print(name, "outer boss radius approx: max dist of outline pts within 2.6mm of hole =", d[(d > 1.3) & (d < 2.8)].max().round(3), " min:", d[(d > 1.3) & (d < 2.8)].min().round(3))
# top surface heightmap of the left lobe
print("\nLeft lobe top heights (max Z) on a grid:")
for y in np.arange(0.5, 9.6, 1.0):
    row = []
    for x in np.arange(-0.5, 8.6, 1.0):
        z = ray_z(corner, x, y)
        row.append(f"{z.max():5.2f}" if len(z) else "  -  ")
    print(f"Y={y:4.1f} " + " ".join(row))
print("X cols:", np.arange(-0.5, 8.6, 1.0))
print("\nLeft lobe bottom heights (min Z):")
for y in np.arange(0.5, 9.6, 1.0):
    row = []
    for x in np.arange(-0.5, 8.6, 1.0):
        z = ray_z(corner, x, y)
        row.append(f"{z.min():5.2f}" if len(z) else "  -  ")
    print(f"Y={y:4.1f} " + " ".join(row))
