"""Daftar objek di sebuah GLB: nama, ukuran, pusat, jumlah segitiga, warna material.
blender --background --factory-startup --python tools/blender_probe_glb.py -- <file.glb>
"""
import sys
import bpy
from mathutils import Vector

path = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=path)
obs = [o for o in bpy.data.objects if o.type == "MESH"]
allpts = []
for ob in sorted(obs, key=lambda o: o.name):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    allpts += pts
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    col = ""
    if ob.active_material and ob.active_material.node_tree:
        bsdf = ob.active_material.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            c = bsdf.inputs["Base Color"].default_value
            col = "#%02x%02x%02x" % tuple(int(v * 255) for v in c[:3])
    s, m = mx - mn, (mx + mn) / 2
    print(f"OBJ {ob.name[:38]:38s} uk=({s.x:7.4f},{s.y:7.4f},{s.z:7.4f}) pusat=({m.x:7.4f},{m.y:7.4f},{m.z:7.4f}) tri={len(ob.data.polygons):7d} {col}")
mn = Vector([min(p[i] for p in allpts) for i in range(3)])
mx = Vector([max(p[i] for p in allpts) for i in range(3)])
print(f"TOTAL {len(obs)} objek, min={tuple(round(v, 4) for v in mn)} max={tuple(round(v, 4) for v in mx)}")
