"""Ekstrak roda 6-spoke (velg + ban) dari racing_raw.glb ke models/web/wheel-6spoke.glb.
Tersedia dua mesh terpisah di dalam GLB: 'rim' dan 'tire'.
Pusat di (0,0,0), sumbu as roda di Z (muka luar menghadap +Z).
Skala disesuaikan ke satuan simulator Mini 4WD (diameter ban 30.2 mm -> R ~ 2.05).
"""
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

SRC = Path("models/work/racing_raw.glb")
OUT = Path("models/web/wheel-6spoke.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SRC))

rim_ob = bpy.data.objects.get("Front Rims:1")
tire_ob = bpy.data.objects.get("Front Tire:1")

# Hapus objek lain
for o in list(bpy.data.objects):
    if o not in (rim_ob, tire_ob):
        bpy.data.objects.remove(o, do_unlink=True)

# Terapkan world matrix ke data mesh masing-masing
for ob in (rim_ob, tire_ob):
    ob.data.transform(ob.matrix_world)
    ob.matrix_world = Matrix.Identity(4)

# Hitung pusat velg langsung dari verteks mesh
verts = [v.co for v in rim_ob.data.vertices]
mn = Vector([min(v[i] for v in verts) for i in range(3)])
mx = Vector([max(v[i] for v in verts) for i in range(3)])
center = (mn + mx) / 2
print(f"Pusat velg terhitung: {center}")

# Sumbu roda asli mengarah ke X (luar = -X, dalam/hub = +X)
# Di simulator: as roda di Z, luar menghadap +Z
# Skala: meter -> mm (x1000) -> simulator (x0.1359174) = x135.9174
SCALE = 1000.0 * 0.1359174

# Transformasi: geser ke tengah, putar agar -X menjadi +Z, lalu skala
# Rotasi 90 derajat di Y: (+Z -> +X, +X -> -Z), atau rotasi -90 di Y: (-X -> +Z)
rot = Matrix.Rotation(math.radians(-90), 4, "Y")
trans = Matrix.Translation(-center)
scale_mat = Matrix.Scale(SCALE, 4)

xf = scale_mat @ rot @ trans

for ob, name in ((rim_ob, "rim"), (tire_ob, "tire")):
    ob.name = name
    ob.data.name = name
    ob.data.transform(xf)
    # Shade smooth dan set sharp
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
