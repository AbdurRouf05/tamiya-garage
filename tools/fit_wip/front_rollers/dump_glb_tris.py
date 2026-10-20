"""Dump triangles of every mesh in a GLB to .npy in glTF (sim) axes: (x, y_up, z)."""
import sys, bpy, numpy as np
args = sys.argv[sys.argv.index("--") + 1:]
path, out = args[0], args[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=path)
allt = []
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    me = o.data
    me.calc_loop_triangles()
    M = o.matrix_world
    co = np.array([tuple(M @ v.co) for v in me.vertices])
    idx = np.array([tuple(t.vertices) for t in me.loop_triangles])
    t = co[idx]  # blender z-up
    allt.append(np.stack([t[..., 0], t[..., 2], -t[..., 1]], -1))
    print("MESH", o.name, len(idx))
np.save(out, np.concatenate(allt))
print("SAVED", out)
