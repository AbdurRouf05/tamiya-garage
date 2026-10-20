"""Pisahkan GLB satu-objek menjadi potongan lepas (loose parts) dan tampilkan yang terbesar.
blender --background --factory-startup --python tools/blender_split_probe.py -- <file.glb> [jumlah]
"""
import sys
import bmesh
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
path, top = args[0], int(args[1]) if len(args) > 1 else 40
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=path)
ob = next(o for o in bpy.data.objects if o.type == "MESH")
bm = bmesh.new()
bm.from_mesh(ob.data)
bm.transform(ob.matrix_world)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bm.faces.ensure_lookup_table()
seen, islands = set(), []
for f in bm.faces:
    if f.index in seen:
        continue
    stack, faces = [f], []
    seen.add(f.index)
    while stack:
        cur = stack.pop()
        faces.append(cur)
        for e in cur.edges:
            for nf in e.link_faces:
                if nf.index not in seen:
                    seen.add(nf.index)
                    stack.append(nf)
    pts = [v.co for fc in faces for v in fc.verts]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    islands.append((len(faces), mn, mx))
islands.sort(key=lambda t: -(t[2] - t[1]).length)
print(f"ISL total {len(islands)} potongan")
for n, mn, mx in islands[:top]:
    s, c = mx - mn, (mx + mn) / 2
    print(f"ISL tri={n:7d} uk=({s.x:6.1f},{s.y:6.1f},{s.z:6.1f}) pusat=({c.x:7.1f},{c.y:7.1f},{c.z:7.1f})")
