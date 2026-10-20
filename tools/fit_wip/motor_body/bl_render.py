"""Generic Workbench renderer.  blender -b --factory-startup --python bl_render.py -- spec.json
spec = {"objects":[{"path":..., "kind":"stl|glb|npz", "color":[r,g,b], "alpha":1, "matrix":[[4x4]] (Blender space),
                    "npz_key": "name" (for npz: arrays name__v (gltf Y-up) and name__f)}, {"prim":"cyl","r":..,"depth":..,"loc":[..],"rot":[..]}...],
        "cams":[{"out":..., "loc":[..], "rot_deg":[..], "ortho":.., "res":[w,h], "persp_lens": optional}],
        "xray": false}"""
import json, math, sys
import bpy, bmesh
import numpy as np
from mathutils import Matrix, Vector
spec = json.load(open(sys.argv[sys.argv.index("--") + 1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
mats = {}
def material(col, alpha):
    key = (tuple(col), alpha)
    if key not in mats:
        m = bpy.data.materials.new(str(key)); m.diffuse_color = (*col, alpha); mats[key] = m
    return mats[key]
for o in spec["objects"]:
    obs = []
    if o.get("prim") == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(radius=o["r"], depth=o["depth"], location=o["loc"], rotation=[math.radians(a) for a in o.get("rot", [0, 0, 0])], vertices=48)
        obs = [bpy.context.object]
    elif o.get("prim") == "box":
        bpy.ops.mesh.primitive_cube_add(size=1, location=o["loc"])
        ob = bpy.context.object; ob.scale = o["size"]; obs = [ob]
    elif o.get("prim") == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=o["r"], location=o["loc"]); obs = [bpy.context.object]
    elif o["kind"] == "stl":
        before = set(bpy.data.objects); bpy.ops.wm.stl_import(filepath=o["path"]); obs = list(set(bpy.data.objects) - before)
    elif o["kind"] == "glb":
        before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=o["path"]); obs = [x for x in set(bpy.data.objects) - before if x.type == "MESH"]
        if o.get("only"):
            for x in list(obs):
                if x.name not in o["only"]:
                    bpy.data.objects.remove(x); obs.remove(x)
    elif o["kind"] == "npz":
        d = np.load(o["path"]); k = o["npz_key"]
        v = d[k + "__v"]; f = d[k + "__f"]
        vb = np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])
        me = bpy.data.meshes.new(k); me.from_pydata(vb.tolist(), [], f.tolist()); me.update()
        ob = bpy.data.objects.new(k, me); bpy.context.scene.collection.objects.link(ob); obs = [ob]
    for ob in obs:
        if "matrix" in o:
            ob.matrix_world = Matrix(o["matrix"]) @ ob.matrix_world
        ob.data.materials.clear(); ob.data.materials.append(material(o.get("color", [0.7, 0.7, 0.7]), o.get("alpha", 1.0)))
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_cavity = True
scene.display.shading.show_xray = spec.get("xray", False)
scene.display.shading.xray_alpha = spec.get("xray_alpha", 0.6)
scene.display.shading.show_object_outline = True
scene.display.shading.light = "STUDIO"
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
for c in spec["cams"]:
    cam.location = Vector(c["loc"])
    if "target" in c:
        cam.rotation_euler = (Vector(c["target"]) - cam.location).to_track_quat("-Z", "Y").to_euler()
    else:
        cam.rotation_euler = [math.radians(a) for a in c["rot_deg"]]
    if c.get("persp_lens"):
        cam.data.type = "PERSP"; cam.data.lens = c["persp_lens"]
    else:
        cam.data.type = "ORTHO"; cam.data.ortho_scale = c["ortho"]
    cam.data.clip_start = 0.01; cam.data.clip_end = 10000
    scene.render.resolution_x, scene.render.resolution_y = c["res"]
    scene.render.filepath = c["out"]
    bpy.ops.render.render(write_still=True)
    print("RENDER", c["out"])
