"""Ekstrak plat terminal kuningan/tembaga dan saklar dari racing_raw.glb.
Menghasilkan:
- models/web/terminals.glb & .js:
  - Terminal kontak dinamo & saklar
  - Terminal jembatan baterai depan
  - Tuas saklar on/off
"""
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

RAW = Path("models/work/racing_raw.glb")
OUT = Path("models/web/terminals.glb")
S = 0.1359174
SCALE = 1000.0 * S

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(RAW))

keep_names = ["Terminal B:1", "Terminal:1", "Terminal C:1", "Switch:1"]
keep_obs = [bpy.data.objects.get(n) for n in keep_names if bpy.data.objects.get(n)]

for o in list(bpy.data.objects):
    if o not in keep_obs:
        bpy.data.objects.remove(o, do_unlink=True)

# Skala meter -> mm -> simulator scale
for ob in keep_obs:
    ob.matrix_world = Matrix.Scale(SCALE, 4) @ ob.matrix_world

# Hitung pusat bersama dan pusatkan
all_mid = sum((sum([Vector(b) for b in o.bound_box], Vector()) / 8.0 for o in keep_obs), Vector()) / len(keep_obs)
for ob in keep_obs:
    ob.location -= all_mid
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    try:
        ob.data.shade_smooth()
        ob.data.set_sharp_from_angle(angle=math.radians(35))
    except AttributeError:
        pass

OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=str(OUT), export_format="GLB", export_yup=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14, export_draco_normal_quantization=10,
    export_materials="NONE",
)
print("Ekspor terminals selesai ->", OUT)
