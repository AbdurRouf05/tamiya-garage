"""Membuat model 3D presisi Baterai AA (Rechargeable NiMH / Alkaline) berdasarkan CAD Battery.SLDPRT.
Dimensi CAD:
- Diameter tabung: 14.2 mm (R = 7.1 mm * S ~ 0.965 satuan sim)
- Panjang total: 50.0 mm (L = 50.0 mm * S ~ 6.80 satuan sim)
- Terminal positif (+) tonjolan (nub): diameter 5.0 mm, tinggi 1.8 mm di +X
- Terminal negatif (-) piringan datar dengan lekukan tepi di -X
- Objek terpisah:
  1. 'body' (selubung label baterai Neo-Champ / Alkaline)
  2. 'terminals' (ujung logam positif dan negatif)
- Sumbu panjang baterai pada sumbu X (sesuai penempatan sasis Tamiya), terpusat di (0,0,0).
"""
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Matrix, Vector

OUT = Path("models/web/battery-aa.glb")
S = 0.1359174  # mm -> simulator scale

bpy.ops.wm.read_factory_settings(use_empty=True)

r_cell = 7.1 * S      # diameter 14.2 mm standar AA
length = 48.2 * S     # panjang tabung selubung
x2 = length / 2.0
r_nub = 2.6 * S       # kutub positif diameter 5.2 mm
h_nub = 1.8 * S       # tonjolan positif

# 1. BODY (SELUBUNG TABUNG)
bpy.ops.mesh.primitive_cylinder_add(
    radius=r_cell,
    depth=length,
    vertices=32,
    location=(0, 0, 0)
)
body_obj = bpy.context.active_object
body_obj.name = "body"
body_obj.data.name = "body"
# Putar ke sumbu X
body_obj.rotation_euler = (0, math.radians(90), 0)
bpy.ops.object.transform_apply(rotation=True)

# 2. TERMINALS (KUTUB LOGAM + & -)
# A. Kutub positif (+) di +X
bpy.ops.mesh.primitive_cylinder_add(
    radius=r_nub,
    depth=h_nub,
    vertices=24,
    location=(x2 + h_nub / 2.0, 0, 0)
)
nub_obj = bpy.context.active_object
nub_obj.rotation_euler = (0, math.radians(90), 0)
bpy.ops.object.transform_apply(rotation=True)

# B. Piringan kontak negatif (-) di -X
bpy.ops.mesh.primitive_cylinder_add(
    radius=r_cell * 0.85,
    depth=0.8 * S,
    vertices=24,
    location=(-x2 - 0.4 * S, 0, 0)
)
base_obj = bpy.context.active_object
base_obj.rotation_euler = (0, math.radians(90), 0)
bpy.ops.object.transform_apply(rotation=True)

# Gabungkan kontak positif dan negatif menjadi 'terminals'
bpy.context.view_layer.objects.active = nub_obj
nub_obj.select_set(True)
base_obj.select_set(True)
bpy.ops.object.join()
nub_obj.name = "terminals"
nub_obj.data.name = "terminals"

for ob in (body_obj, nub_obj):
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.shade_smooth()
    print(f"Object {ob.name}: {len(ob.data.polygons):,} segitiga")

OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=str(OUT), export_format="GLB", export_yup=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14, export_draco_normal_quantization=10,
    export_materials="NONE",
)
print("Ekspor battery-aa selesai ->", OUT)
