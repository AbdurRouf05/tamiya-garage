import numpy as np, sys
from PIL import Image, ImageDraw
from vox import Grid
g = Grid([14, -1, 3], [64, 36, 24], 0.1)
z = np.load(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].endswith(".npz") else np.load("cache/vox_file.npz")
names = sys.argv[2].split(",") if len(sys.argv) > 2 else ["ch"]
zs = [float(v) for v in sys.argv[3].split(",")]
xr = (22, 57); yr = (5, 30)
out = sys.argv[4]
COL = {"ch": (170, 170, 175), "cv": (240, 120, 30), "kn": (40, 120, 240)}
def ix(ax, v): return int(round((v - g.lo[ax]) / g.h))
tiles = []
S = 4
for zz in zs:
    k = ix(2, zz)
    sub = {n: z[n][ix(0, xr[0]):ix(0, xr[1]), ix(1, yr[0]):ix(1, yr[1]), k] for n in names}
    shp = next(iter(sub.values())).shape
    img = np.full(shp + (3,), 25, np.uint8); cnt = np.zeros(shp, int)
    for n, s in sub.items():
        img[s] = COL[n]; cnt += s
    img[cnt > 1] = (255, 0, 0)
    img = np.transpose(img, (1, 0, 2))[::-1]
    im = Image.fromarray(img).resize((shp[0] * S, shp[1] * S), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for mm in range(xr[0], xr[1] + 1):
        x = (mm - xr[0]) * 10 * S
        d.line([(x, 0), (x, im.size[1])], fill=(60, 60, 60) if mm % 5 else (140, 140, 40))
        if mm % 5 == 0: d.text((x + 2, im.size[1] - 12), str(mm), fill=(255, 255, 0))
    for mm in range(yr[0], yr[1] + 1):
        y = im.size[1] - (mm - yr[0]) * 10 * S
        d.line([(0, y), (im.size[0], y)], fill=(60, 60, 60) if mm % 5 else (140, 140, 40))
        if mm % 5 == 0: d.text((2, y - 12), str(mm), fill=(255, 255, 0))
    d.text((40, 4), f"Z={zz}", fill=(255, 255, 255))
    tiles.append(im)
cols = 2
w, h = tiles[0].size
M = Image.new("RGB", (w * cols, h * ((len(tiles) + cols - 1) // cols)), (0, 0, 0))
for i, t in enumerate(tiles):
    M.paste(t, ((i % cols) * w, (i // cols) * h))
M.save(out); print(out, M.size)
