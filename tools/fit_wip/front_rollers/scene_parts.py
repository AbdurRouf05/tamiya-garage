"""Common scene (STL mm frame of the chassis, Z-up): chassis, bodies, tyres, sim placements."""
import sys
from pathlib import Path
HERE = Path(r"C:/Users/arack/AppData/Local/Temp/claude/D--coding-cozy-village/bb2493d4-aa52-4045-a5e2-0a655a382ec3/scratchpad/wf/front_rollers")
sys.path.insert(0, str(HERE))
import numpy as np
from stlslice import tris, to_sim, to_stl, S, R

AX, W, TR, TW = 5.4, 4.55, 1.75, 1.45


def sim2stl_tris(T):
    return to_stl(T.reshape(-1, 3)).reshape(T.shape)


def magnum_tris():
    t = np.load(HERE / "magnum_tris.npy")
    car = np.stack([t[..., 0], t[..., 1] + R + 0.1, t[..., 2] * 1.12], -1)
    return car  # car-local sim


def sayap_tris():
    t = np.load(HERE / "aero_tris.npy")
    car = np.stack([-1.05 * t[..., 0] - 0.15, 1.28 * t[..., 1] + 1.3, -1.12 * t[..., 2]], -1)
    return car


def sample_surface(T, density=40.0, seed=0):
    """Random points on triangles, ~density points per unit^2 (in T's units), min 1 per tri + vertices."""
    rng = np.random.default_rng(seed)
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    n = np.maximum(1, np.ceil(area * density)).astype(int)
    idx = np.repeat(np.arange(len(T)), n)
    u, v = rng.random(len(idx)), rng.random(len(idx))
    f = u + v > 1
    u[f], v[f] = 1 - u[f], 1 - v[f]
    P = a[idx] + u[:, None] * (b[idx] - a[idx]) + v[:, None] * (c[idx] - a[idx])
    return np.vstack([P, T.reshape(-1, 3)])
