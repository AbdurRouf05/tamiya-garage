"""Dump every mesh of a GLB to npz in glTF (Y-up) coordinates, world transforms applied.
blender --background --factory-startup --python bl_dump_glb.py -- <in.glb> <out.npz>"""
import sys
import bpy
import numpy as np
a = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a[0])
out = {}
for ob in bpy.data.objects:
    if ob.type != "MESH":
        continue
    me = ob.data
    me.calc_loop_triangles()
    v = np.array([ob.matrix_world @ x.co for x in me.vertices], dtype=np.float64)
    f = np.array([t.vertices[:] for t in me.loop_triangles], dtype=np.int64)
    # Blender Z-up -> glTF Y-up: (x, y, z)_bl -> (x, z, -y)_gltf
    vg = np.column_stack([v[:, 0], v[:, 2], -v[:, 1]])
    name = ob.data.name if ob.name.startswith("Mesh") else ob.name
    out[ob.name + "__v"] = vg
    out[ob.name + "__f"] = f
    print("DUMP", ob.name, ob.data.name, len(vg), len(f), vg.min(0).round(3), vg.max(0).round(3))
np.savez(a[1], **out)
