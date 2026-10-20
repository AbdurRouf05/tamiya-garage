"""Perkecil dinamo FA-130 (hasil konversi STEP) dan ubah ke satuan simulator.
blender --background --factory-startup --python tools/blender_fa130.py -- <fa130_raw.glb> <out.glb>

File asli dalam meter, poros searah sumbu Y Blender (setelah ekspor Y-atas menjadi sumbu Z simulator,
yaitu arah melintang seperti dinamo pada sasis dinamo belakang).
"""
import math
import sys

import bpy
from mathutils import Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
obs = [o for o in bpy.data.objects if o.type == "MESH"]
for o in bpy.data.objects:
    o.select_set(o in obs)
bpy.context.view_layer.objects.active = obs[0]
if len(obs) > 1:
    bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = ob.data
me.transform(Matrix.Scale(1000 * 0.1346, 4))        # meter -> mm -> satuan simulator

# Sisi poros: titik yang dekat sumbu (radius < 1,2 mm) di ujung-ujung Y
r = 1.2 * 0.1346
pos = [v.co.y for v in me.vertices if math.hypot(v.co.x, v.co.z) < r]
ymax = max(v.co.y for v in me.vertices)
plus = sum(1 for y in pos if y > ymax * 0.7)
minus = sum(1 for y in pos if y < -ymax * 0.7)
print(f"FA130 titik poros di +Y: {plus}, di -Y: {minus}")

n0 = len(me.polygons)
mod = ob.modifiers.new("dec", "DECIMATE")
mod.ratio = 40000 / n0
bpy.ops.object.modifier_apply(modifier="dec")
try:
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(30))
except AttributeError:
    pass
ob.name = "fa130"
print(f"FA130 {n0} -> {len(ob.data.polygons)} segitiga")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_yup=True, export_apply=True,
                          export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
                          export_draco_position_quantization=14, export_draco_normal_quantization=10,
                          export_materials="NONE")
