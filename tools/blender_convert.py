"""Ubah STL sumber menjadi satu GLB ringan (Draco) dalam satuan dan arah simulator.

blender --background --factory-startup --python tools/blender_convert.py -- \
    <out.glb> <skala> <ox,oy,oz> <rotasi_z_derajat> "<file.stl>|<nama>|<target_segitiga>[|<koreksi>]" ...

Setiap STL digeser (titik asal -> ox,oy,oz), diputar di sumbu Z, diskala, dilas
(merge by distance), diperkecil dengan Decimate, lalu dihaluskan berdasarkan sudut.

<koreksi> (opsional, dalam mm STL) memindahkan part ke posisi rakitnya SEBELUM transform di atas,
untuk part yang di file-nya diletakkan untuk dicetak, bukan terpasang:
    "dx,dy,dz"                          -> geser
    "dx,dy,dz;rx,ry,rz;px,py,pz"        -> putar (derajat, urutan X lalu Y lalu Z) di sekitar titik p, lalu geser
"""
import math
import sys

import bmesh
import bpy
from mathutils import Matrix

args = sys.argv[sys.argv.index("--") + 1:]
out_path, scale, origin, rot = args[0], float(args[1]), [float(v) for v in args[2].split(",")], float(args[3])
items = args[4:]

bpy.ops.wm.read_factory_settings(use_empty=True)
xf = Matrix.Scale(scale, 4) @ Matrix.Rotation(math.radians(rot), 4, "Z") @ Matrix.Translation([-v for v in origin])

def correction(spec):
    """Matriks koreksi posisi rakit (mm STL): putar di sekitar pivot, lalu geser."""
    parts = spec.split(";")
    move = Matrix.Translation([float(v) for v in parts[0].split(",")])
    if len(parts) == 1:
        return move
    rx, ry, rz = (math.radians(float(v)) for v in parts[1].split(","))
    pivot = [float(v) for v in parts[2].split(",")] if len(parts) > 2 else [0, 0, 0]
    rot = Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(ry, 4, "Y") @ Matrix.Rotation(rx, 4, "X")
    return move @ Matrix.Translation(pivot) @ rot @ Matrix.Translation([-v for v in pivot])


for item in items:
    fields = item.split("|")
    path, name, target = fields[0], fields[1], int(fields[2])
    fix = correction(fields[3]) if len(fields) > 3 and fields[3] else Matrix.Identity(4)
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=path)
    ob = (set(bpy.data.objects) - before).pop()
    ob.name = name
    me = ob.data
    me.transform(xf @ fix)
    n0, v0 = len(me.polygons), len(me.vertices)

    # STL sering menyimpan titik ganda per segitiga; las dulu agar Decimate bekerja rapi
    if v0 > n0 * 0.9:
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
        bm.to_mesh(me)
        bm.free()

    if len(me.polygons) > target:
        mod = ob.modifiers.new("dec", "DECIMATE")
        mod.ratio = target / len(me.polygons)
        mod.use_collapse_triangulate = True
        dg = bpy.context.evaluated_depsgraph_get()
        new_me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        ob.modifiers.remove(mod)
        ob.data = new_me
        bpy.data.meshes.remove(me)
        me = new_me
    me.name = name

    try:
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(32))
    except AttributeError:
        pass
    print(f"CONVERT {name:28s} {n0:>10,} -> {len(me.polygons):>8,} segitiga (titik awal {v0:,})")

bpy.ops.export_scene.gltf(
    filepath=out_path, export_format="GLB", export_yup=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14, export_draco_normal_quantization=10,
    export_materials="NONE",
)
print("CONVERT selesai ->", out_path)
