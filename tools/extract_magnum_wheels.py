"""Ekstrak roda 5-spoke spiral (velg + ban) dari Cyclone Magnum (magnum_raw.glb)
menjadi models/web/wheel-cyclone.glb dan wheel-cyclone.js.
Sumbu as roda di Z, muka luar velg menghadap +Z, titik tengah di (0,0,0).
Skala disesuaikan ke satuan simulator.
"""
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Matrix, Vector

SRC = Path("models/work/magnum_raw.glb")
OUT = Path("models/web/wheel-cyclone.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SRC))

ob = bpy.data.objects[0]
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0001)
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")

# Cari tire belakang kiri (Y > -348) dan velg belakang kiri
WHEEL_X, MID_Y, AXLE_Z = 133.39, -348.06, 171.30
tire_ob = None
rim_compound = None

for o in bpy.data.objects:
    pts = [Vector(c) for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    c, s = (mn + mx) / 2, mx - mn
    # Ban belakang kiri: dekat WHEEL_X, Z dekat AXLE_Z, Y > MID_Y, diameter ~56.8, tebal ~28.4
    if abs(c.x - WHEEL_X) < 2 and abs(c.z - AXLE_Z) < 2 and c.y > MID_Y and abs(s.x - 56.8) < 2:
        tire_ob = o
    # Velg gabungan: lebar melintasi sasis (s.y > 100)
    elif abs(c.x - WHEEL_X) < 2 and abs(c.z - AXLE_Z) < 2 and s.y > 100:
        rim_compound = o

print("Tire ob:", tire_ob.name if tire_ob else None)
print("Rim compound:", rim_compound.name if rim_compound else None)

if not tire_ob or not rim_compound:
    raise RuntimeError("Tidak dapat menemukan objek roda di magnum_raw.glb")

# Pisahkan rim_compound menjadi sisi kiri saja (Y > MID_Y)
bpy.context.view_layer.objects.active = rim_compound
rim_compound.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(rim_compound.data)
verts_to_delete = [v for v in bm.verts if v.co.y < MID_Y + 5.0]
bmesh.ops.delete(bm, geom=verts_to_delete, context="VERTS")
bmesh.update_edit_mesh(rim_compound.data)
bpy.ops.object.mode_set(mode="OBJECT")

# Hapus semua objek lain kecuali tire_ob dan rim_compound
for o in list(bpy.data.objects):
    if o not in (tire_ob, rim_compound):
        bpy.data.objects.remove(o, do_unlink=True)

# Hitung pusat tire
verts = [v.co for v in tire_ob.data.vertices]
mn = Vector([min(v[i] for v in verts) for i in range(3)])
mx = Vector([max(v[i] for v in verts) for i in range(3)])
center = (mn + mx) / 2
print(f"Pusat roda Magnum asli: {center}")

# Sumbu roda asli adalah sumbu Y file IGES!
# Luar menghadap +Y (kiri)
# Di simulator: sumbu as roda di Z, luar menghadap +Z
# Rotasi: +Y -> +Z (putar -90 derajat di X: (X, Y, Z) -> (X, -Z, Y), atau putar 90 di X: (X, Z, -Y))
# Untuk Y -> +Z: rotasi di sumbu X sebesar 90 derajat:
# Vector(0, 1, 0) setelah rotasi X(+90) adalah (0, 0, 1)!
rot = Matrix.Rotation(math.radians(90), 4, "X")
trans = Matrix.Translation(-center)

# Skala Magnum: skala jarak sumbu roda 80 mm / 206.87 mm * 0.1359174 = 0.052562
SCALE = (80.0 / 206.87) * 0.1359174
scale_mat = Matrix.Scale(SCALE, 4)

xf = scale_mat @ rot @ trans

for ob, name in ((rim_compound, "rim"), (tire_ob, "tire")):
    ob.name = name
    ob.data.name = name
    ob.data.transform(xf)
    # Decimate jika terlalu rapat
    if len(ob.data.polygons) > 8000:
        mod = ob.modifiers.new("dec", "DECIMATE")
        mod.ratio = 8000.0 / len(ob.data.polygons)
        dg = bpy.context.evaluated_depsgraph_get()
        new_me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        ob.modifiers.remove(mod)
        ob.data = new_me
        ob.data.name = name
    try:
        ob.data.shade_smooth()
        ob.data.set_sharp_from_angle(angle=math.radians(35))
    except AttributeError:
        pass
    print(f"Mesh {name}: {len(ob.data.polygons):,} segitiga")

OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=str(OUT), export_format="GLB", export_yup=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14, export_draco_normal_quantization=10,
    export_materials="NONE",
)
print("Ekspor selesai ->", OUT)
