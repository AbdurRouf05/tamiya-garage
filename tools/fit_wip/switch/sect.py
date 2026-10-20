import numpy as np, sys
from PIL import Image, ImageDraw
from vox import Grid
COL = {"ch": (170, 170, 175), "cv": (240, 120, 30), "kn": (40, 120, 240)}
def section(g, vols, ax, val, fn, scale=8, title=""):
    """vols: dict name->bool array. ax: 0 (YZ plane, horiz=Y, vert=Z), 1 (XZ, horiz=X), 2 (XY, horiz=X vert=Y)"""
    k = int(round((val - g.lo[ax]) / g.h))
    sl = {n: np.take(v, k, axis=ax) for n, v in vols.items()}
    shp = next(iter(sl.values())).shape  # (h_axis, v_axis)
    img = np.full(shp + (3,), 25, np.uint8)
    cnt = np.zeros(shp, int)
    for n, s in sl.items():
        img[s] = COL[n]; cnt += s
    img[cnt > 1] = (255, 0, 0)
    img = np.transpose(img, (1, 0, 2))[::-1]  # vertical axis up
    im = Image.fromarray(img).resize((shp[0] * scale // 1, shp[1] * scale // 1), Image.NEAREST)
    d = ImageDraw.Draw(im)
    axes = [a for a in range(3) if a != ax]
    hlo = g.lo[axes[0]]; vlo = g.lo[axes[1]]
    H, V = shp
    # 1mm grid ticks, 5mm lines
    for mm in range(int(np.ceil(hlo)), int(hlo + H * g.h) + 1):
        x = (mm - hlo) / g.h * scale
        if mm % 5 == 0:
            d.line([(x, 0), (x, im.size[1])], fill=(80, 80, 80) if mm % 10 else (120, 120, 60), width=1)
            d.text((x + 2, im.size[1] - 12), str(mm), fill=(255, 255, 0))
    for mm in range(int(np.ceil(vlo)), int(vlo + V * g.h) + 1):
        y = im.size[1] - (mm - vlo) / g.h * scale
        if mm % 5 == 0:
            d.line([(0, y), (im.size[0], y)], fill=(80, 80, 80) if mm % 10 else (120, 120, 60), width=1)
            d.text((2, y - 12), str(mm), fill=(255, 255, 0))
    names = "XYZ"
    d.text((10, 10), f"{title} section {names[ax]}={val}  horiz={names[axes[0]]} vert={names[axes[1]]}  gray=chassis orange=cover blue=knob RED=overlap", fill=(255, 255, 255))
    im.save(fn)
    return fn
