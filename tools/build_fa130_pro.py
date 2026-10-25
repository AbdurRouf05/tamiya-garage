"""Membuat model 3D dinamo Mabuchi FA-130 PRO Double Shaft (untuk sasis MS/MA mid-ship).
Fitur utama:
- Sumbu poros ganda (double shaft) menonjol simetris di kedua ujung (+Y dan -Y)
- Dudukan bearing collar di kedua sisi
- Kompresi Draco untuk web
"""
import math
from pathlib import Path
import bpy

SRC = Path("models/web/fa130.glb")
OUT = Path("models/web/fa130-pro.glb")
S = 0.1359174  # mm -> simulator scale

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SRC))

ob = [o for o in bpy.data.objects if o.type == "MESH"][0]
bpy.context.view_layer.objects.active = ob

# Shaft ganda tembus dari -2.7 hingga +2.7 (panjang 5.4 simulator unit)
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0 * S,
    depth=5.4,
    vertices=24,
    location=(0, 0, 0)
)
shaft_cyl = bpy.context.active_object
shaft_cyl.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)

# Bearing collar tambahan di sisi belakang (-Y)
bpy.ops.mesh.primitive_cylinder_add(
    radius=2.8 * S,
    depth=1.6 * S,
    vertices=24,
    location=(0, -1.82, 0)
)
rear_collar = bpy.context.active_object
rear_collar.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)

# Gabungkan menjadi satu objek fa130-pro
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
shaft_cyl.select_set(True)
rear_collar.select_set(True)
bpy.ops.object.join()
ob.name = "fa130-pro"

# Sedikit decimate untuk optimasi ukuran web (target ~35k segitiga)
n0 = len(ob.data.polygons)
if n0 > 35000:
    mod = ob.modifiers.new("dec", "DECIMATE")
    mod.ratio = 35000 / n0
    bpy.ops.object.modifier_apply(modifier="dec")

print(f"fa130-pro {n0} -> {len(ob.data.polygons)} segitiga")

OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=str(OUT), export_format="GLB", export_yup=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14, export_draco_normal_quantization=10,
    export_materials="NONE",
)
print("Ekspor fa130-pro selesai ->", OUT)
