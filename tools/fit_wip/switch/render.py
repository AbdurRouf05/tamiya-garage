"""blender --background --factory-startup --python render.py -- <out_prefix> <json_spec>
spec: {"parts":[{"file":..,"color":[r,g,b],"loc":[dx,dy,dz],"rot":[rx,ry,rz] (deg, about pivot),"pivot":[x,y,z],"alpha":1}],
       "views":[{"name":..,"dir":"side|top|bottom|front|back|iso|side_l","center":[x,y,z],"scale":s,"res":[w,h]}],
       "markers":[[x,y,z,r,[col]]], "clip": optional}"""
import math, sys, json
from pathlib import Path
import bpy
from mathutils import Vector, Euler, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
spec = json.loads(Path(args[1]).read_text())
src = Path(r"D:\coding\tamiya-garage\models\source\super1-printables")
bpy.ops.wm.read_factory_settings(use_empty=True)
for i, p in enumerate(spec["parts"]):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(src / p["file"]))
    ob = (set(bpy.data.objects) - before).pop()
    m = bpy.data.materials.new(f"m{i}")
    a = p.get("alpha", 1.0)
    m.diffuse_color = (*p["color"], a)
    ob.data.materials.append(m)
    piv = Vector(p.get("pivot", [0, 0, 0]))
    rot = [math.radians(r) for r in p.get("rot", [0, 0, 0])]
    R = Euler(rot, 'XYZ').to_matrix().to_4x4()
    T = Matrix.Translation(Vector(p.get("loc", [0, 0, 0])))
    ob.matrix_world = T @ Matrix.Translation(piv) @ R @ Matrix.Translation(-piv)
    if "bisect" in p:
        # keep only geometry on one side: [axis, value, keep_greater]
        import bmesh
        ax, val, keep_gt = p["bisect"]
        bm = bmesh.new(); bm.from_mesh(ob.data)
        no = [0, 0, 0]; no[ax] = 1
        co = [0, 0, 0]; co[ax] = val
        # in object space (matrix applied later is world) -> apply world first
        bm.transform(ob.matrix_world); ob.matrix_world = Matrix()
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no,
                               clear_inner=keep_gt, clear_outer=not keep_gt)
        bm.to_mesh(ob.data); bm.free()
for mk in spec.get("markers", []):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=mk[3], location=mk[:3])
    s = bpy.context.object
    m = bpy.data.materials.new("mk")
    m.diffuse_color = (*mk[4], 1)
    s.data.materials.append(m)
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_cavity = True
scene.display.shading.show_object_outline = True
scene.display.shading.show_xray = spec.get("xray", False)
scene.display.shading.xray_alpha = 0.5
scene.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.type = "ORTHO"
cam.data.clip_start = 0.1
cam.data.clip_end = 2000
D = 300
dirs = {
  "side":   ((1, 0, 0), (90, 0, 90)),     # from +X looking -X, up +Z, right=+Y
  "side_l": ((-1, 0, 0), (90, 0, -90)),   # from -X looking +X, right=-Y
  "top":    ((0, 0, 1), (0, 0, 0)),       # from +Z, right=+X, up=+Y
  "bottom": ((0, 0, -1), (180, 0, 0)),    # from -Z, right=+X, up=-Y
  "front":  ((0, -1, 0), (90, 0, 0)),     # from -Y looking +Y, right=+X, up=+Z
  "back":   ((0, 1, 0), (90, 0, 180)),    # from +Y looking -Y, right=-X
}
for v in spec["views"]:
    c = Vector(v["center"])
    if v["dir"] == "iso":
        d = Vector(v.get("vec", (1, -1, 0.8))).normalized()
        cam.location = c + d * D
        cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    else:
        d, r = dirs[v["dir"]]
        cam.location = c + Vector(d) * D
        cam.rotation_euler = tuple(math.radians(a) for a in r)
    if "clip" in v:
        cam.data.clip_start = D - v["clip"]
    else:
        cam.data.clip_start = 0.1
    cam.data.ortho_scale = v["scale"]
    scene.render.resolution_x, scene.render.resolution_y = v.get("res", (1200, 900))
    scene.render.filepath = f"{out}_{v['name']}.png"
    bpy.ops.render.render(write_still=True)
    print("RENDER", scene.render.filepath)
