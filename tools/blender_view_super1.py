"""Render ortografis sasis Super-1 + bearing asli (merah) dari samping dan atas, dengan grid mm.
blender --background --factory-startup --python tools/blender_view_super1.py -- <folder_keluaran>
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

out = Path(sys.argv[sys.argv.index("--") + 1])
src = Path(__file__).resolve().parent.parent / "models" / "source" / "super1-printables"
bpy.ops.wm.read_factory_settings(use_empty=True)


def load(name, color):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(src / name))
    ob = (set(bpy.data.objects) - before).pop()
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    ob.data.materials.append(m)
    return ob


load("chassis-super-1.stl", (0.75, 0.75, 0.78))
load("chassis-super-1-wheel-bearing.stl", (0.95, 0.1, 0.1))
# Penanda pusat lubang (bola hijau kecil) setiap 10 mm sepanjang y pada tinggi as z=15,1
for y in range(0, 130, 10):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(80, y, 15.1))
    s = bpy.context.object
    m = bpy.data.materials.new(f"m{y}")
    m.diffuse_color = (0.1, 0.8, 0.2, 1) if y % 20 == 0 else (0.1, 0.4, 0.9, 1)
    s.data.materials.append(m)

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_cavity = True
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.type = "ORTHO"
for name, loc, scale, res in (("samping", (140, 61, 15), 130, (1600, 560)),):
    cam.location = Vector(loc)
    cam.rotation_euler = (math.radians(90), 0, math.radians(90))   # menghadap -X, atas = +Z
    cam.data.ortho_scale = scale
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = str(out / f"super1_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDER", scene.render.filepath)
