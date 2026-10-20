"""FFT search: rigid translation of (bracket+cover) w.r.t. chassis. overlap volume & contact area for every shift (0.4 mm grid)."""
import numpy as np, common
from scipy import ndimage
from scipy.signal import fftconvolve
g = common.Grid()
def load(p): return np.unpackbits(np.load(common.CACHE / f"occ_{p}.npy"))[: g.n.prod()].reshape(g.n).astype(bool)
ch = load("chassis"); mb = load("motor-bracket"); gc = load("gear-cover")
def down(a):  # 0.2 -> 0.4 mm (any)
    n = (np.array(a.shape) // 2) * 2
    a = a[: n[0], : n[1], : n[2]]
    return a.reshape(n[0] // 2, 2, n[1] // 2, 2, n[2] // 2, 2).mean((1, 3, 5))
C = down(ch).astype(np.float32)          # fraction occupancy
C = (C > 0.5).astype(np.float32)
Cd = ndimage.binary_dilation(C > 0, iterations=1).astype(np.float32)
res = {}
for name, A0 in (("bracket", mb), ("bracket+cover", mb | gc)):
    A = (down(A0) > 0.5).astype(np.float32)
    # crop A to bbox
    idx = np.argwhere(A > 0); lo = idx.min(0); hi = idx.max(0) + 1
    Ac = A[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
    K = Ac[::-1, ::-1, ::-1]
    ov = fftconvolve(C, K, mode="full")
    ct = fftconvolve(Cd, K, mode="full") - ov
    # full-mode index i corresponds to placing Ac's origin at i - (Ksize-1); shift relative to file position = (i - (Ksize-1)) - lo
    ks = np.array(Ac.shape)
    def shift_of(i): return (np.array(i) - (ks - 1) - lo) * 0.4
    # restrict to shifts within ranges
    rng = {"x": (-4, 4), "y": (-6, 24), "z": (-8, 8)}
    best = []
    I = np.indices(ov.shape, sparse=True)
    sx = (I[0] - (ks[0] - 1) - lo[0]) * 0.4; sy = (I[1] - (ks[1] - 1) - lo[1]) * 0.4; sz = (I[2] - (ks[2] - 1) - lo[2]) * 0.4
    m = (sx >= rng["x"][0]) & (sx <= rng["x"][1]) & (sy >= rng["y"][0]) & (sy <= rng["y"][1]) & (sz >= rng["z"][0]) & (sz <= rng["z"][1])
    ovm = np.where(m, ov, np.inf); ctm = np.where(m, ct, -np.inf)
    np.save(common.CACHE / f"fit_{name}.npy", np.stack([np.where(m, ov, -1), np.where(m, ct, -1)]))
    print(f"== {name}: Ksize {ks}, lo {lo}")
    # file position
    i0 = tuple((ks - 1 + lo).astype(int))
    print(f"  file position: overlap {ov[i0]*0.064:.1f} mm3  contact {ct[i0]*0.4*0.4:.1f} mm2 (approx)")
    # candidates: overlap < 2 voxels, sort by contact
    ok = m & (ov < 1.5)
    cand = np.argwhere(ok)
    sc = ct[ok]
    order = np.argsort(-sc)[:25]
    for k in order:
        i = cand[k]; s = shift_of(i)
        print(f"  shift dX {s[0]:+5.1f} dY {s[1]:+5.1f} dZ {s[2]:+5.1f}  overlap {ov[tuple(i)]:.1f} vox  contact {sc[k]:.0f} vox")
