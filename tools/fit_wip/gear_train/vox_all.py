import common, numpy as np, time
g = common.Grid()
print("grid", g.n)
for n in ["", "-gear-cover", "-motor-bracket", "-rear-bumper"]:
    t0 = time.time()
    occ, odd = common.voxelize(common.tris(n), g)
    key = n.strip("-") or "chassis"
    np.save(common.CACHE / f"occ_{key}.npy", np.packbits(occ, axis=None))
    print(key, "odd cols", odd, "vox", occ.sum(), "vol mm3", round(occ.sum() * g.h**3, 1), round(time.time() - t0, 1), "s")
