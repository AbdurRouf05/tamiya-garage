from scene_parts import *
from stlslice import ray_z
ch = tris("chassis-super-1.stl")
holes = {"A": (2.005, 6.262), "B": (4.474, 3.115)}
top = {k: ray_z(ch, x, y + (0.0)) for k, (x, y) in holes.items()}
# boss top right at hole edge (hole itself is empty above its floor) -> sample ring at r=1.5
boss_top = {}
for k, (x, y) in holes.items():
    zs = []
    for a in np.linspace(0, 2 * np.pi, 24, endpoint=False):
        z = ray_z(ch, x + 1.5 * np.cos(a), y + 1.5 * np.sin(a))
        if len(z):
            zs.append(z.max())
    boss_top[k] = (min(zs), max(zs), float(np.mean(zs)))
    print(f"hole {k}: floor Z={top[k]}, boss top around hole (r=1.5 ring) Z min {min(zs):.3f} max {max(zs):.3f} mean {np.mean(zs):.3f}")

bodies = {"Magnum": sample_surface(magnum_tris(), 400), "SayapS1": sample_surface(sayap_tris(), 400)}
for bn, P in bodies.items():
    Q = to_stl(P)  # mm
    print(f"\n== {bn}: {len(Q)} surface samples; bbox mm X {Q[:,0].min():.2f}..{Q[:,0].max():.2f} Y {Q[:,1].min():.2f}..{Q[:,1].max():.2f} Z {Q[:,2].min():.2f}..{Q[:,2].max():.2f}")
    for side, mirror in (("L", False), ("R", True)):
        for k, (hx, hy) in holes.items():
            if mirror:
                hx = 78.029 - hx  # measured R holes at 76.024 / 73.555 (symmetric about X=39.0145)
            for rname, rr_mm in (("sim r0.65", 0.65 / S), ("13mm true", 6.5)):
                for plate in (0.0, 1.5):
                    zb = boss_top[k][1] + plate
                    zt = zb + 0.72 / S   # sim roller height 0.72 units = 5.35 mm
                    d = np.hypot(Q[:, 0] - hx, Q[:, 1] - hy)
                    inband = (Q[:, 2] >= zb) & (Q[:, 2] <= zt)
                    inside = inband & (d < rr_mm)
                    hclear = (d[inband] - rr_mm).min() if inband.any() else np.inf
                    above = (d < rr_mm) & (Q[:, 2] > zt)
                    vclear = (Q[above, 2] - zt).min() if above.any() else np.inf
                    print(f"  {side}{k} {rname:9s} plate {plate:.1f}mm: roller Z {zb:.2f}..{zt:.2f}  body pts inside={inside.sum():5d}  "
                          f"min horiz gap in band={hclear:6.2f} mm  min gap above roller top={vclear:6.2f} mm")
