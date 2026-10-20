"""Exact mesh section outlines. python section.py <axis x|y|z> <val> [--win a0,a1,b0,b1] [--ppm 20] [--part name:dx,dy,dz] ... [--tag t] [--circ y,z,r,color]...
parts default chassis, gear-cover, motor-bracket at file positions; --part overrides list (name or name:dx,dy,dz)."""
import sys, numpy as np, common
from PIL import Image, ImageDraw, ImageFont
COL = {"chassis": (90, 90, 95), "gear-cover": (220, 30, 30), "motor-bracket": (30, 80, 230), "rear-bumper": (30, 160, 60), "switch-cover": (200, 120, 0), "battery-retainer": (120, 0, 160)}

def segments(t, axis, val):
    d = t[:, :, axis] - val
    s = np.sign(d)
    m = ~((s > 0).all(1) | (s < 0).all(1))
    t, d = t[m], d[m]
    out = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        di, dj = d[:, i], d[:, j]
        cross = (di * dj < 0)
        w = np.where(cross, di / np.where(cross, di - dj, 1), np.nan)
        p = t[:, i] + (t[:, j] - t[:, i]) * w[:, None]
        out.append(p)
    P = np.stack(out, 1)  # (n,3 edges,3)
    ok = ~np.isnan(P[:, :, 0])
    good = ok.sum(1) == 2
    P, ok = P[good], ok[good]
    idx = np.argsort(~ok, axis=1, kind="stable")[:, :2]
    a = P[np.arange(len(P)), idx[:, 0]]; b = P[np.arange(len(P)), idx[:, 1]]
    return a, b

def main(argv):
    axis = "xyz".index(argv[0]); val = float(argv[1])
    win = None; ppm = 20; parts = []; tag = "sec"; circs = []; marks = []
    i = 2
    while i < len(argv):
        if argv[i] == "--win": win = [float(x) for x in argv[i + 1].split(",")]; i += 2
        elif argv[i] == "--ppm": ppm = float(argv[i + 1]); i += 2
        elif argv[i] == "--part":
            nm, *sh = argv[i + 1].split(":"); parts.append((nm, [float(x) for x in sh[0].split(",")] if sh else [0, 0, 0])); i += 2
        elif argv[i] == "--tag": tag = argv[i + 1]; i += 2
        elif argv[i] == "--circ": circs.append([float(x) for x in argv[i + 1].split(",")[:3]] + [argv[i + 1].split(",")[3] if len(argv[i + 1].split(",")) > 3 else "orange"]); i += 2
        elif argv[i] == "--mark": marks.append([float(x) for x in argv[i + 1].split(",")]); i += 2
        else: raise SystemExit("bad arg " + argv[i])
    if not parts: parts = [("chassis", [0, 0, 0]), ("gear-cover", [0, 0, 0]), ("motor-bracket", [0, 0, 0])]
    hz, vt = {0: (1, 2), 1: (0, 2), 2: (1, 0)}[axis]
    a0, a1, b0, b1 = win
    W, H = int((a1 - a0) * ppm), int((b1 - b0) * ppm)
    pad = 40
    im = Image.new("RGB", (W + 2 * pad, H + 2 * pad + 20), "white"); d = ImageDraw.Draw(im)
    tx = lambda u: pad + (u - a0) * ppm; ty = lambda v: pad + (b1 - v) * ppm
    for t_ in np.arange(np.ceil(a0), a1 + 1e-6):
        maj = round(t_) % 10 == 0; mid = round(t_) % 5 == 0
        d.line([(tx(t_), pad), (tx(t_), pad + H)], fill=(0, 0, 0) if maj else (200, 200, 200) if mid else (238, 238, 238))
        if maj or (ppm >= 30 and mid): d.text((tx(t_) - 6, pad + H + 3), f"{t_:.0f}", fill="black"); d.text((tx(t_) - 6, pad - 14), f"{t_:.0f}", fill="black")
    for t_ in np.arange(np.ceil(b0), b1 + 1e-6):
        maj = round(t_) % 10 == 0; mid = round(t_) % 5 == 0
        d.line([(pad, ty(t_)), (pad + W, ty(t_))], fill=(0, 0, 0) if maj else (200, 200, 200) if mid else (238, 238, 238))
        if maj or (ppm >= 30 and mid): d.text((2, ty(t_) - 5), f"{t_:.0f}", fill="black")
    for nm, sh in parts:
        t = common.tris(nm if nm != "chassis" else "").astype(np.float64) + np.array(sh)
        a, b = segments(t, axis, val)
        for p, q in zip(a, b):
            d.line([(tx(p[hz]), ty(p[vt])), (tx(q[hz]), ty(q[vt]))], fill=COL.get(nm, (0, 0, 0)), width=2)
    for c in circs:
        u, v, r, col = c
        d.ellipse([tx(u - r), ty(v + r), tx(u + r), ty(v - r)], outline=col, width=2)
        d.line([(tx(u) - 4, ty(v)), (tx(u) + 4, ty(v))], fill=col); d.line([(tx(u), ty(v) - 4), (tx(u), ty(v) + 4)], fill=col)
    for m in marks:
        d.ellipse([tx(m[0]) - 4, ty(m[1]) - 4, tx(m[0]) + 4, ty(m[1]) + 4], fill=(0, 170, 0))
    an = "XYZ"
    d.text((pad, pad + H + 18), f"{an[axis]}={val}  horiz={an[hz]}  vert={an[vt]}  parts={parts}", fill="black")
    fn = common.WF / f"{tag}_{an[axis]}{val:g}.png"; im.save(fn); print(fn)

if __name__ == "__main__":
    main(sys.argv[1:])
