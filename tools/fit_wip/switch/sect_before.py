import numpy as np
from vox import Grid
from sect import section
g = Grid([14, -1, 3], [64, 36, 24], 0.1)
z = np.load("cache/vox_file.npz"); vols = {k: z[k] for k in ("ch", "cv", "kn")}
out = "renders/sec_before"
for ax, vals, sc in ((0, [25.2, 39.0, 45.6, 52.8], 4), (1, [9.3, 12.0, 15.0, 18.5, 21.0], 4), (2, [5.5, 6.5, 8.0, 10.0, 12.0, 14.0], 4)):
    for v in vals:
        print(section(g, vols, ax, v, f"{out}_{'XYZ'[ax]}{v}.png", sc, "FILE POS"))
