"""List loose pieces of body-magnum.glb (sim units, glTF Y-up -> Blender Z-up on import)."""
import sys, bpy
from mathutils import Vector
path = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=path)
obs = [o for o in bpy.data.objects if o.type == "MESH"]
print("OBJECTS", [(o.name, len(o.data.polygons)) for o in obs])
ob = obs[0]
bpy.context.view_layer.objects.active = ob
for o in obs: o.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0005)
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")
rows = []
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    pts = [o.matrix_world @ v.co for v in o.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    s, c = mx - mn, (mx + mn) / 2
    rows.append((max(s), o.name, s, c, len(o.data.polygons)))
rows.sort()
print("N pieces", len(rows))
# Blender Z-up: sim (x, y, z) = (bx, bz, -by)
for m, n, s, c, f in rows:
    if m < 4.0:
        print(f"PIECE {n:20s} size_blender=({s.x:6.3f},{s.y:6.3f},{s.z:6.3f}) centre_sim=({c.x:7.3f},{c.z:7.3f},{-c.y:7.3f}) faces={f}")
print("LARGEST", [(n, tuple(round(v,2) for v in s), tuple(round(v,2) for v in (c.x, c.z, -c.y))) for m, n, s, c, f in rows[-6:]])
