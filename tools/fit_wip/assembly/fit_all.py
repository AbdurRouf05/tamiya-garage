"""Uji semua part pelengkap Super-1 terhadap sasis: overlap (mm3) dan kontak (mm3 part dalam jarak h dari sasis)
di posisi file, di geser bersama T0, dan pencarian FFT translasi terbaik dalam +-R mm di sekitar T0.
python fit_all.py [h_search] [R]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rear_bumper"))
from slicer import transformed
from voxel import voxelize
import numpy as np
from scipy.signal import fftconvolve
from scipy.ndimage import binary_dilation

T0 = np.array([0.977, 13.96, 0.0])
PARTS = ["rear-bumper", "gear-cover", "motor-bracket", "switch-cover", "switch-on-off", "battery-retainer", "wheel-bearing"]
J = np.array([0.00731, 0.00517, 0.00293])
hs = float(sys.argv[1]) if len(sys.argv) > 1 else 0.2
R = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5
CH = transformed("chassis-super-1")

def crop_xy(t, lo, hi):
    """Ambil segitiga sasis yang menyentuh kolom XY [lo,hi]; semua Z dipertahankan supaya paritas sinar Z tetap benar."""
    mn = t[:, :, :2].min(1); mx = t[:, :, :2].max(1)
    return t[np.all((mx >= lo[:2]) & (mn <= hi[:2]), axis=1)]

def measure(tp, h=0.1, pad=1.0):
    lo = tp.reshape(-1, 3).min(0) - pad; hi = tp.reshape(-1, 3).max(0) + pad
    org = np.floor(lo / h) * h + J
    shape = tuple(np.ceil((hi - org) / h).astype(int))
    C = voxelize(crop_xy(CH, org, org + np.array(shape) * h), org, h, shape)
    B = voxelize(tp, org, h, shape)
    sh = binary_dilation(C) & ~C
    return (C & B).sum() * h**3, (sh & B).sum() * h**3, B.sum() * h**3

for p in PARTS:
    t = transformed("chassis-super-1-" + p)
    o0, c0, vol = measure(t)
    o1, c1, _ = measure(t + T0)
    # FFT search on grid: translations T0 + k*hs, |k*hs| <= R
    h = hs
    lo = t.reshape(-1, 3).min(0) - h; hi = t.reshape(-1, 3).max(0) + h
    borg = np.floor(lo / h) * h + J
    bshape = tuple(np.ceil((hi - borg) / h).astype(int))
    B = voxelize(t, borg, h, bshape).astype(np.float32)
    n = int(round(R / h)) + 2
    corg = borg + T0 - n * h
    cshape = tuple(np.array(bshape) + 2 * n)
    C = voxelize(crop_xy(CH, corg, corg + np.array(cshape) * h), corg, h, cshape)
    shell = (binary_dilation(C) & ~C).astype(np.float32)
    Bf = B[::-1, ::-1, ::-1]
    ov = fftconvolve(C.astype(np.float32), Bf, mode="valid")   # index k -> shift (k - n)*h
    ct = fftconvolve(shell, Bf, mode="valid")
    k = np.indices(ov.shape).reshape(3, -1).T - n
    s = k * h
    m = np.all(np.abs(s) <= R + 1e-9, axis=1)
    o = ov.reshape(-1)[m] * h**3; c = ct.reshape(-1)[m] * h**3; ss = s[m] + T0
    print(f"\n== {p}: vol {vol:.1f} mm3 | file pos: overlap {o0:.2f} kontak {c0:.2f} | T0 {tuple(T0)}: overlap {o1:.2f} kontak {c1:.2f}")
    for thr in (0.2, 1.0):
        ki = np.nonzero(o <= thr)[0]
        best = ki[np.argsort(-c[ki])[:6]]
        print(f"   overlap<={thr} (h={h}) kontak teratas:", "  ".join(f"({a:.2f},{b:.2f},{d:.2f}) o={oo:.2f} c={cc:.1f}" for (a, b, d), oo, cc in zip(ss[best], o[best], c[best])))
