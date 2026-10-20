"""Generic Blender ortho renderer. blender -b --factory-startup --python brender.py -- config.json
config: {"parts":[{"file":..., "color":[r,g,b], "loc":[dx,dy,dz], "rot":[rx,ry,rz deg], "pivot":[x,y,z], "alpha":1}],
 "markers":[{"loc":[x,y,z],"r":0.6,"color":[..]}], "cyls":[{"loc":..,"r":..,"depth":..,"axis":"X","color":..}],
 "views":[{"name":..., "loc":[..], "rot":[deg..], "scale":..., "res":[w,h], "clip":[start,end]}], "out": dir, "xray":0}"""
import json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector, Matrix, Euler
cfg = json.load(open(sys.argv[sys.argv.index("--") + 1]))
out = Path(cfg["out"])
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name, color, alpha=1.0):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, alpha); return m
for i, p in enumerate(cfg["parts"]):
    before = set(bpy.data.objects)
    if p["file"].lower().endswith(".stl"):
        bpy.ops.wm.stl_import(filepath=p["file"])
    else:
        bpy.ops.import_scene.gltf(filepath=p["file"])
    obs = [o for o in set(bpy.data.objects) - before if o.type == "MESH"]
    for ob in obs:
        ob.data.materials.clear(); ob.data.materials.append(mat(f"m{i}", p.get("color", (0.7, 0.7, 0.7)), p.get("alpha", 1.0)))
        piv = Vector(p.get("pivot", (0, 0, 0)))
        R = Euler([math.radians(a) for a in p.get("rot", (0, 0, 0))]).to_matrix().to_4x4()
        M = Matrix.Translation(Vector(p.get("loc", (0, 0, 0))) + piv) @ R @ Matrix.Translation(-piv)
        if "matrix" in p: M = Matrix(p["matrix"])
        ob.matrix_world = M @ ob.matrix_world
for j, mk in enumerate(cfg.get("markers", [])):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=mk.get("r", 0.6), location=mk["loc"])
    bpy.context.object.data.materials.append(mat(f"k{j}", mk.get("color", (0.1, 0.8, 0.2))))
for j, c in enumerate(cfg.get("cyls", [])):
    rot = {"X": (0, math.pi / 2, 0), "Y": (math.pi / 2, 0, 0), "Z": (0, 0, 0)}[c.get("axis", "X")]
    bpy.ops.mesh.primitive_cylinder_add(radius=c["r"], depth=c["depth"], location=c["loc"], rotation=rot, vertices=64)
    bpy.context.object.data.materials.append(mat(f"c{j}", c.get("color", (0.9, 0.8, 0.1)), c.get("alpha", 1.0)))
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.color_type = "MATERIAL"; sh.show_cavity = True; sh.light = "STUDIO"
if cfg.get("xray"): sh.show_xray = True; sh.xray_alpha = cfg["xray"]
sh.show_backface_culling = False
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new("w"); scene.world.color = (1, 1, 1)
sh.background_type = "VIEWPORT"; sh.background_color = (1, 1, 1)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
cam.data.type = "ORTHO"
for v in cfg["views"]:
    if "target" in v:
        d = Vector(v["dir"]).normalized(); cam.location = Vector(v["target"]) + d * v.get("dist", 200)
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        if "roll" in v: cam.rotation_euler.rotate_axis("Z", math.radians(v["roll"]))
    else:
        cam.location = Vector(v["loc"]); cam.rotation_euler = [math.radians(a) for a in v["rot"]]
    cam.data.ortho_scale = v["scale"]
    cs, ce = v.get("clip", (0.1, 1000)); cam.data.clip_start = cs; cam.data.clip_end = ce
    scene.render.resolution_x, scene.render.resolution_y = v.get("res", (1200, 800))
    scene.render.filepath = str(out / f"{v['name']}.png")
    bpy.ops.render.render(write_still=True); print("RENDER", scene.render.filepath)
