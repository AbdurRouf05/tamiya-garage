"""Plane slicing of STL parts, loop extraction, circle fitting, PNG drawing."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, __import__("os").path.dirname(__file__))
from stlio import tris

AX = {"x": 0, "y": 1, "z": 2}

def transformed(name, T=None):
    t = tris(name).astype(np.float64)
    if T is not None:
        sh = t.shape
        v = t.reshape(-1, 3)
        v = v @ T[:3, :3].T + T[:3, 3]
        t = v.reshape(sh)
    return t

def section(t, axis, val):
    """returns segments (n,2,3) of intersection of triangles with plane coord[axis]=val"""
    a = AX[axis]
    d = t[:, :, a] - val
    s = np.sign(d)
    s[s == 0] = 1e-9
    m = ~((s > 0).all(1) | (s < 0).all(1))
    tt, dd = t[m], d[m]
    segs = []
    pts = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        di, dj = dd[:, i], dd[:, j]
        cross = (di * dj) < 0
        w = np.where(cross, di / np.where(cross, di - dj, 1), np.nan)
        p = tt[:, i] + (tt[:, j] - tt[:, i]) * w[:, None]
        pts.append(p)
    pts = np.stack(pts, 1)  # (n,3 edges,3)
    ok = ~np.isnan(pts[:, :, 0])
    cnt = ok.sum(1)
    sel = cnt == 2
    P = pts[sel]; O = ok[sel]
    idx = np.argsort(~O, axis=1, kind="stable")[:, :2]
    seg = np.take_along_axis(P, idx[:, :, None], axis=1)
    return seg

def loops(seg, axis, tol=1e-3):
    """group segments into connected components; return list of point arrays (2D)"""
    a = AX[axis]; keep = [i for i in range(3) if i != a]
    s2 = seg[:, :, keep]
    if len(s2) == 0:
        return []
    k = np.round(s2.reshape(-1, 2) / tol).astype(np.int64)
    _, inv = np.unique(k, axis=0, return_inverse=True)
    inv = inv.reshape(-1, 2)
    n = inv.max() + 1
    parent = np.arange(n)
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for u, v in inv:
        ru, rv = find(u), find(v)
        if ru != rv: parent[ru] = rv
    roots = np.array([find(i) for i in range(n)])
    comp = roots[inv[:, 0]]
    out = []
    for c in np.unique(comp):
        out.append(s2[comp == c].reshape(-1, 2))
    return out

def fitcircle(p):
    x, y = p[:, 0], p[:, 1]
    A = np.column_stack([x, y, np.ones_like(x)])
    b = x * x + y * y
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = c[0] / 2, c[1] / 2
    r = np.sqrt(c[2] + cx * cx + cy * cy)
    res = np.abs(np.hypot(x - cx, y - cy) - r).max()
    return cx, cy, r, res

def circles(seg, axis, rmax=6, resmax=0.05):
    out = []
    for p in loops(seg, axis):
        if len(p) < 12: continue
        cx, cy, r, res = fitcircle(p)
        if r < rmax and res < resmax:
            out.append((cx, cy, r, res, len(p)))
    return out

def draw(layers, axis, val, rng, ppm, path, marks=(), title=""):
    """layers: list of (seg, (r,g,b)). rng: ((u0,u1),(v0,v1)) in plane coords (the 2 remaining axes in order)."""
    a = AX[axis]; keep = [i for i in range(3) if i != a]
    (u0, u1), (v0, v1) = rng
    W, H = int((u1 - u0) * ppm), int((v1 - v0) * ppm)
    im = Image.new("RGB", (W, H + 30), (255, 255, 255)); d = ImageDraw.Draw(im)
    def P(u, v): return ((u - u0) * ppm, H - (v - v0) * ppm)
    for g in np.arange(np.ceil(u0), u1 + 1e-9, 1.0):
        x, _ = P(g, v0); col = (150, 150, 150) if g % 10 == 0 else ((205, 205, 205) if g % 5 == 0 else (235, 235, 235))
        d.line([(x, 0), (x, H)], fill=col)
        if g % 10 == 0: d.text((x + 2, H + 2), f"{g:.0f}", fill=(0, 0, 0))
    for g in np.arange(np.ceil(v0), v1 + 1e-9, 1.0):
        _, y = P(u0, g); col = (150, 150, 150) if g % 10 == 0 else ((205, 205, 205) if g % 5 == 0 else (235, 235, 235))
        d.line([(0, y), (W, y)], fill=col)
        if g % 10 == 0: d.text((2, y + 2), f"{g:.0f}", fill=(0, 0, 0))
    for seg, col in layers:
        s2 = seg[:, :, keep]
        for (p, q) in s2:
            d.line([P(*p), P(*q)], fill=col, width=2)
    for (u, v, r, col) in marks:
        x, y = P(u, v); d.ellipse([x - r * ppm, y - r * ppm, x + r * ppm, y + r * ppm], outline=col, width=1)
        d.line([(x - 4, y), (x + 4, y)], fill=col); d.line([(x, y - 4), (x, y + 4)], fill=col)
    names = "XYZ"
    d.text((5, H + 15), f"{title}  section {names[a]}={val}  horiz={names[keep[0]]} vert={names[keep[1]]}  grid 1mm (labels every 10)", fill=(0, 0, 0))
    im.save(path)
