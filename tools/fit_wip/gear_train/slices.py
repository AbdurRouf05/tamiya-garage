"""Cross-section images from voxel grids. usage: python slices.py axis(x|y|z) v1 v2 ... [--parts chassis,gear-cover,motor-bracket] [--shift part:dx,dy,dz] [--tag name] [--win a0,a1,b0,b1]"""
import sys, numpy as np, common
from PIL import Image, ImageDraw, ImageFont
g = common.Grid()
args = sys.argv[1:]
axis = "xyz".index(args[0]); vals = []; parts = ["chassis", "gear-cover", "motor-bracket"]; shifts = {}; tag = "s"; win = None; scale = 6
i = 1
while i < len(args):
    if args[i] == "--parts": parts = args[i + 1].split(","); i += 2
    elif args[i] == "--shift":
        k, v = args[i + 1].split(":"); shifts[k] = [float(x) for x in v.split(",")]; i += 2
    elif args[i] == "--tag": tag = args[i + 1]; i += 2
    elif args[i] == "--win": win = [float(x) for x in args[i + 1].split(",")]; i += 2
    elif args[i] == "--scale": scale = int(args[i + 1]); i += 2
    else: vals.append(float(args[i])); i += 1
COL = {"chassis": (150, 150, 155), "gear-cover": (230, 60, 60), "motor-bracket": (60, 110, 230), "rear-bumper": (60, 180, 80)}
occ = {}
for p in parts:
    o = np.unpackbits(np.load(common.CACHE / f"occ_{p}.npy"))[: g.n.prod()].reshape(g.n).astype(bool)
    if p in shifts:
        s = np.round(np.array(shifts[p]) / g.h).astype(int)
        o = np.roll(o, s, axis=(0, 1, 2))
    occ[p] = o
other = [a for a in range(3) if a != axis]  # image horizontal = other[0]? choose: x-slice -> (Y right, Z up); y-slice -> (X right, Z up); z-slice -> (Y right, X up)
if axis == 0: hz, vt = 1, 2
elif axis == 1: hz, vt = 0, 2
else: hz, vt = 1, 0
font = ImageFont.load_default()
for v in vals:
    k = int((v - g.lo[axis]) / g.h)
    sl = {p: np.take(o, k, axis=axis) for p, o in occ.items()}  # 2D in remaining axes order
    # remaining order: sorted(other); make array [h, v]
    def hv(a):
        rem = [x for x in range(3) if x != axis]
        return a if rem == [hz, vt] else a.T
    H, V = g.n[hz], g.n[vt]
    img = np.full((V, H, 3), 255, np.uint8)
    cnt = np.zeros((H, V), int)
    for p in parts:
        m = hv(sl[p]); cnt += m
        img[::-1][m.T] = COL[p]
    img[::-1][(cnt >= 2).T] = (255, 0, 255)
    im = Image.fromarray(img)
    a0, a1, b0, b1 = win if win else (g.lo[hz], g.lo[hz] + H * g.h, g.lo[vt], g.lo[vt] + V * g.h)
    # crop
    c0, c1 = int((a0 - g.lo[hz]) / g.h), int((a1 - g.lo[hz]) / g.h)
    r0, r1 = V - int((b1 - g.lo[vt]) / g.h), V - int((b0 - g.lo[vt]) / g.h)
    im = im.crop((c0, r0, c1, r1)).resize(((c1 - c0) * scale, (r1 - r0) * scale), Image.NEAREST)
    pad = 40
    canvas = Image.new("RGB", (im.width + 2 * pad, im.height + 2 * pad), "white")
    canvas.paste(im, (pad, pad))
    d = ImageDraw.Draw(canvas)
    px = scale / g.h
    for t in np.arange(np.ceil(a0), a1 + 1e-6, 1.0):
        X = pad + (t - a0) * px
        major = abs(t % 10) < 1e-6 or abs(t % 10 - 10) < 1e-6
        if major or abs(t % 5) < 1e-6:
            d.line([(X, pad), (X, pad + im.height)], fill=(0, 0, 0) if major else (190, 190, 190), width=1)
        if major: d.text((X - 6, pad + im.height + 4), f"{t:.0f}", fill="black", font=font); d.text((X - 6, 4), f"{t:.0f}", fill="black", font=font)
    for t in np.arange(np.ceil(b0), b1 + 1e-6, 1.0):
        Y = pad + (b1 - t) * px
        major = abs(t % 10) < 1e-6 or abs(t % 10 - 10) < 1e-6
        if major or abs(t % 5) < 1e-6:
            d.line([(pad, Y), (pad + im.width, Y)], fill=(0, 0, 0) if major else (190, 190, 190), width=1)
        if major: d.text((2, Y - 5), f"{t:.0f}", fill="black", font=font)
    an = "XYZ"
    d.text((pad, pad + im.height + 20), f"{an[axis]}={v}  horiz={an[hz]} vert={an[vt]}  grey=chassis red=gear-cover blue=bracket green=bumper magenta=overlap  shifts={shifts}", fill="black", font=font)
    fn = common.WF / f"{tag}_{an[axis]}{v:g}.png"
    canvas.save(fn); print(fn)
