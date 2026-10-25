"""Membuat model 3D presisi Mass Damper (Pemberat Kuningan Tamiya Mini 4WD).
Standar Tamiya:
- Pemberat kuningan (weight): silinder bertingkat diameter 8.5 mm (bawah) dan 6.0 mm (leher atas),
  tinggi 6.0 mm, lubang pemandu 2.1 mm.
- Tiang pemandu (guide pole): tiang stainless steel diameter 2.0 mm, tinggi 13.0 mm sepanjang sumbu Y.
- Locknut atas: mur pengunci M2 heksagonal (kunci 4 mm) di puncak tiang.
- Bola stabilizer plastik di atas mur.
- Ring bantalan bawah (spacer washer): diameter 4.5 mm, tebal 1.0 mm.
- Sumbu vertikal Y, terpusat di (0,0,0) pada dasar pemasangan.
"""
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Matrix, Vector

OUT = Path("models/web/mass-damper.glb")
S = 0.1359174  # mm -> simulator scale

bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. PEMBERAT KUNINGAN (WEIGHT)
# Profil berputar mengelilingi sumbu Y
weight_mesh = bpy.data.meshes.new("damper_weight")
weight_obj = bpy.data.objects.new("damper_weight", weight_mesh)
bpy.context.scene.collection.objects.link(weight_obj)

bm = bmesh.new()
r_hole = 1.05 * S
r_bot = 4.25 * S
r_top = 3.0 * S
h_bot = 3.8 * S
h_tot = 6.0 * S
y_float = 2.0 * S  # mengambang 2 mm di atas dasar

pts = [
    Vector((r_hole, y_float, 0)),
    Vector((r_bot, y_float, 0)),
    Vector((r_bot, y_float + h_bot, 0)),
    Vector((r_top, y_float + h_bot, 0)),
    Vector((r_top, y_float + h_tot, 0)),
    Vector((r_hole, y_float + h_tot, 0)),
]
verts = [bm.verts.new(p) for p in pts]
bm.faces.new(verts)

bmesh.ops.spin(
    bm,
    geom=bm.faces[:] + bm.edges[:] + bm.verts[:],
    axis=Vector((0, 1, 0)),
    cent=Vector((0, 0, 0)),
    angle=2.0 * math.pi,
    steps=32,
    use_merge=True,
    use_duplicate=False,
)
bm.to_mesh(weight_mesh)
bm.free()

# 2. TIANG PEMANDU & LOCKNUT (POLE & NUT) SEPANJANG SUMBU Y
pole_h = 13.0 * S
r_pole = 0.95 * S

# Silinder tiang vertikal (putar 90 deg ke sumbu Y)
bpy.ops.mesh.primitive_cylinder_add(
    radius=r_pole,
    depth=pole_h,
    vertices=20,
    location=(0, pole_h / 2.0, 0)
)
cyl = bpy.context.active_object
cyl.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)

# Spacer bawah
bpy.ops.mesh.primitive_cylinder_add(
    radius=2.2 * S,
    depth=1.2 * S,
    vertices=24,
    location=(0, 0.6 * S, 0)
)
washer = bpy.context.active_object
washer.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)

# Mur pengunci heksagonal di puncak tiang
bpy.ops.mesh.primitive_cylinder_add(
    radius=2.2 * S,
    depth=1.8 * S,
    vertices=6,
    location=(0, pole_h - 0.9 * S, 0)
)
nut = bpy.context.active_object
nut.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)

# Bola stabilizer plastik di atas mur
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.0 * S,
    segments=24,
    ring_count=16,
    location=(0, pole_h + 1.2 * S, 0)
)
ball = bpy.context.active_object

# Gabungkan bagian tiang & locknut
bpy.context.view_layer.objects.active = cyl
for o in (washer, nut, ball):
    o.select_set(True)
cyl.select_set(True)
bpy.ops.object.join()
cyl.name = "damper_pole"
cyl.data.name = "damper_pole"

for ob in (weight_obj, cyl):
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
print("Ekspor mass-damper selesai ->", OUT)
