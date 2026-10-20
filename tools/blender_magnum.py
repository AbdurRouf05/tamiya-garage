"""Pisahkan model Cyclone Magnum (satu objek IGES) menjadi kelompok part, lalu render pratinjau
atau ekspor GLB.

blender --background --factory-startup --python tools/blender_magnum.py -- <magnum_raw.glb> render <out.png>
blender --background --factory-startup --python tools/blender_magnum.py -- <magnum_raw.glb> export <out.glb>

Kelompok ditentukan dari posisi tiap potongan lepas (satuan file asli, Z-atas setelah impor):
roda di x = 133,4 dan -73,5, garis tengah y = -348,1, tinggi as z = 171,5.
"""
import math
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
src, action, out = args[0], args[1], args[2]
WHEEL_X, MID_Y, AXLE_Z = (133.4, -73.5), -348.1, 171.5
SCALE = 80.0 / (WHEEL_X[0] - WHEEL_X[1]) * 0.1346   # jarak sumbu roda = 80 mm, lalu mm -> satuan simulator

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
ob = next(o for o in bpy.data.objects if o.type == "MESH")
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0001)
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")


def box(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return mn, mx


def classify(o):
    mn, mx = box(o)
    c, s = (mn + mx) / 2, mx - mn
    near_wheel = min(abs(c.x - wx) for wx in WHEEL_X) < 32 and abs(abs(c.y - MID_Y) - 76) < 30 and abs(c.z - AXLE_Z) < 32
    if near_wheel and max(s.x, s.z) < 62:
        return "roda"
    # Velg kiri-kanan yang tersambung as terbaca sebagai satu potongan lebar: tetap roda
    if min(abs(c.x - wx) for wx in WHEEL_X) < 32 and abs(c.z - AXLE_Z) < 32 and max(s.x, s.z) < 62:
        return "roda"
    if s.y > 90 and s.x < 10 and s.z < 10:
        return "as"
    if s.z < 40 and c.z < 180 and s.x > 250:
        return "sasis"
    if max(s) < 12:
        return "sekrup"
    if c.z < 200 and (c.x < WHEEL_X[1] - 25 or c.x > WHEEL_X[0] + 25) and max(s) < 50:
        return "roller"
    return "body"


groups = {}
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    groups.setdefault(classify(o), []).append(o)
for g, obs in sorted(groups.items()):
    print(f"GROUP {g:7s} {len(obs):4d} potongan, {sum(len(o.data.polygons) for o in obs):7d} segitiga")

COLORS = {"body": (0.15, 0.35, 0.95), "roda": (0.1, 0.1, 0.1), "sasis": (0.9, 0.5, 0.1), "as": (0.8, 0.8, 0.8),
          "sekrup": (1, 0, 1), "roller": (0.1, 0.9, 0.3)}

if action == "render":
    for g, obs in groups.items():
        m = bpy.data.materials.new(g)
        m.diffuse_color = (*COLORS[g], 1)
        for o in obs:
            o.data.materials.clear()
            o.data.materials.append(m)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.color_type = "MATERIAL"
    scene.render.resolution_x, scene.render.resolution_y = 1200, 700
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    target = Vector((30, MID_Y, 190))
    cam.location = target + Vector((-260, -320, 230))   # dari depan-kiri-atas
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 40
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("RENDER", out)
else:
    # Ekspor body saja (shell, sayap, sirip), ditempatkan di koordinat simulator
    keep = groups.get("body", [])
    for o in bpy.data.objects:
        o.select_set(o in keep)
    bpy.context.view_layer.objects.active = keep[0]
    bpy.ops.object.join()
    body = bpy.context.view_layer.objects.active
    body.name = "body"
    me = body.data
    # Pusat di tengah kedua as roda, tinggi as = 0; depan model ada di -x, simulator depan di +x
    from mathutils import Matrix
    me.transform(Matrix.Translation((-(WHEEL_X[0] + WHEEL_X[1]) / 2, -MID_Y, -AXLE_Z)))
    me.transform(Matrix.Rotation(math.pi, 4, "Z"))
    me.transform(Matrix.Scale(SCALE, 4))
    n0 = len(me.polygons)
    if n0 > 60000:
        mod = body.modifiers.new("dec", "DECIMATE")
        mod.ratio = 60000 / n0
        bpy.ops.object.modifier_apply(modifier="dec")
    try:
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(32))
    except AttributeError:
        pass
    for o in list(bpy.data.objects):
        if o is not body:
            bpy.data.objects.remove(o)
    print(f"EXPORT body {n0} -> {len(me.polygons)} segitiga")
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_yup=True, export_apply=True,
                              export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
                              export_draco_position_quantization=14, export_draco_normal_quantization=10,
                              export_materials="NONE")
