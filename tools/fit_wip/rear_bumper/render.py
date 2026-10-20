"""blender --background --factory-startup --python render.py -- config.json
config: {"out": dir, "prefix": str, "parts":[{"name":..., "color":[r,g,b,a], "loc":[dx,dy,dz], "rot":[rx,ry,rz deg], "pivot":[x,y,z]}],
         "markers":[[x,y,z,r,[r,g,b]]], "views":[{"name":..., "dir": "top|bottom|side|sideL|rear|front|iso", "center":[x,y,z], "scale": mm, "res":[w,h]}]}"""
import json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector, Euler, Matrix
cfg = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text())
src = Path(r"D:\coding\tamiya-garage\models\source\super1-printables")
out = Path(cfg["out"]); out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
for p in cfg["parts"]:
    before = set(bpy.data.objects)
    fp = p.get("path") or str(src / (p["name"] + ".stl"))
    bpy.ops.wm.stl_import(filepath=fp)
    ob = (set(bpy.data.objects) - before).pop()
    m = bpy.data.materials.new(p["name"]); m.diffuse_color = tuple(p.get("color", [0.7, 0.7, 0.7, 1]))
    ob.data.materials.append(m)
    piv = Vector(p.get("pivot", [0, 0, 0]))
    rot = Euler([math.radians(a) for a in p.get("rot", [0, 0, 0])], "XYZ").to_matrix().to_4x4()
    M = Matrix.Translation(Vector(p.get("loc", [0, 0, 0]))) @ Matrix.Translation(piv) @ rot @ Matrix.Translation(-piv)
    ob.matrix_world = M
for i, mk in enumerate(cfg.get("markers", [])):
    x, y, z, r, col = mk
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z), segments=12, ring_count=8)
    s = bpy.context.object; m = bpy.data.materials.new(f"mk{i}"); m.diffuse_color = (*col, 1); s.data.materials.append(m)
for i, cy in enumerate(cfg.get("cylinders", [])):
    x, y, z, r, h, col = cy
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=(x, y, z), vertices=32)
    s = bpy.context.object; m = bpy.data.materials.new(f"cy{i}"); m.diffuse_color = (*col, 1); s.data.materials.append(m)
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_cavity = True
scene.display.shading.show_xray = cfg.get("xray", False)
scene.display.shading.xray_alpha = cfg.get("xray_alpha", 0.5)
scene.render.film_transparent = False
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
cam.data.type = "ORTHO"; cam.data.clip_start = 0.1; cam.data.clip_end = 2000
D = 300
dirs = {  # (offset dir from center, euler)
    "top": ((0, 0, 1), (0, 0, 0)),               # looking -Z, screen right=+X, up=+Y
    "bottom": ((0, 0, -1), (math.pi, 0, 0)),      # looking +Z, right=+X, up=-Y
    "side": ((1, 0, 0), (math.pi/2, 0, math.pi/2)),   # from +X looking -X, right=+Y, up=+Z
    "sideL": ((-1, 0, 0), (math.pi/2, 0, -math.pi/2)),  # from -X looking +X, right=-Y, up=+Z
    "rear": ((0, 1, 0), (math.pi/2, 0, math.pi)),   # from +Y looking -Y, right=-X, up=+Z
    "front": ((0, -1, 0), (math.pi/2, 0, 0)),       # from -Y looking +Y, right=+X, up=+Z
}
for v in cfg["views"]:
    c = Vector(v["center"])
    if v["dir"] == "iso":
        d = Vector(v.get("vec", (1, 1, 0.8))).normalized()
        cam.location = c + d * D
        cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    else:
        d, e = dirs[v["dir"]]
        cam.location = c + Vector(d) * D; cam.rotation_euler = e
    cam.data.ortho_scale = v["scale"]
    scene.render.resolution_x, scene.render.resolution_y = v.get("res", [1200, 900])
    scene.render.filepath = str(out / f"{cfg['prefix']}_{v['name']}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDER", scene.render.filepath)
