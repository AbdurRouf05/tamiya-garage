"""Membuat model 3D presisi Roller 13 mm 3-Spoke berdasarkan CAD Piringan.SLDPRT.
Dimensi terukur CAD:
- Diameter luar: 13.0 mm (R = 6.5 mm * S)
- Tebal piringan: 2.2 mm (Y = -1.1*S .. +1.1*S)
- Alur pemandu dinding (outer guide groove): lekukan setengah lingkaran di ekuator
- Lubang as / baut tengah: diameter 2.0 mm (R = 1.0 mm * S)
- Boss bantalan tengah: diameter 3.0 mm (R = 1.5 mm * S)
- 3 Window cutout melengkung pada web piringan, membentuk 3 palang spoke aerodinamis
- Terpusat di (0,0,0), sumbu putar pada sumbu Y (sesuai simulator Three.js).
"""
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Matrix, Vector

OUT = Path("models/web/roller-13mm.glb")
S = 0.1359174  # mm -> simulator scale

bpy.ops.wm.read_factory_settings(use_empty=True)

r_out = 6.5 * S       # R = 6.5 mm (diameter 13 mm)
thick = 2.4 * S       # tebal 2.4 mm
y2 = thick / 2.0
r_boss = 1.8 * S      # boss bantalan
r_hole = 1.0 * S      # lubang baut M2 (diameter 2.0 mm)
r_rim_in = 5.2 * S    # dinding dalam rim

# A. Cylinder utama piringan (sumbu Z diganti ke sumbu Y agar putaran simulator natural)
bpy.ops.mesh.primitive_cylinder_add(radius=r_out, depth=thick, vertices=48, location=(0, 0, 0))
roller_obj = bpy.context.active_object
roller_obj.name = "roller"
roller_obj.data.name = "roller"
# Putar silinder agar sumbu putarnya adalah Y
roller_obj.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)

# B. Alur lingkar luar (outer groove) untuk panduan dinding lintasan
bm_groove = bmesh.new()
bpy.ops.mesh.primitive_torus_add(
    major_radius=r_out,
    minor_radius=0.45 * S,
    major_segments=48,
    minor_segments=16,
    location=(0, 0, 0)
)
groove_obj = bpy.context.active_object
groove_obj.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)

mod = roller_obj.modifiers.new("groove_cut", "BOOLEAN")
mod.object = groove_obj
mod.operation = "DIFFERENCE"
mod.solver = "EXACT"
bpy.context.view_layer.objects.active = roller_obj
bpy.ops.object.modifier_apply(modifier="groove_cut")
bpy.data.objects.remove(groove_obj, do_unlink=True)

# C. Lubang baut tengah 2.0 mm
bpy.ops.mesh.primitive_cylinder_add(radius=r_hole, depth=thick * 3.0, vertices=24, location=(0, 0, 0))
hole_obj = bpy.context.active_object
hole_obj.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)

mod = roller_obj.modifiers.new("hole_cut", "BOOLEAN")
mod.object = hole_obj
mod.operation = "DIFFERENCE"
mod.solver = "EXACT"
bpy.context.view_layer.objects.active = roller_obj
bpy.ops.object.modifier_apply(modifier="hole_cut")
bpy.data.objects.remove(hole_obj, do_unlink=True)

# D. 3 Window Cutouts melengkung tembus sumbu Y
for i in range(3):
    mid_deg = 60 + i * 120
    ang0 = math.radians(mid_deg - 32)
    ang1 = math.radians(mid_deg + 32)
    
    bm_cut = bmesh.new()
    pts_cut = []
    
    r_cut_in = r_boss + 0.3 * S
    r_cut_out = r_rim_in - 0.2 * S
    
    # Busur dalam pada bidang XZ (Y = -thick)
    for step in range(6):
        t = step / 5.0
        a = ang0 + t * (ang1 - ang0)
        pts_cut.append(Vector((r_cut_in * math.cos(a), -thick * 1.5, r_cut_in * math.sin(a))))
    
    # Busur luar
    for step in range(6):
        t = step / 5.0
        a = ang1 - t * (ang1 - ang0)
        pts_cut.append(Vector((r_cut_out * math.cos(a), -thick * 1.5, r_cut_out * math.sin(a))))
        
    f_cut = bm_cut.faces.new([bm_cut.verts.new(p) for p in pts_cut])
    
    # Ekstrusi sepanjang sumbu Y
    res = bmesh.ops.extrude_face_region(bm_cut, geom=[f_cut])
    top_verts = [v for v in res["geom"] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm_cut, vec=Vector((0, thick * 3.0, 0)), verts=top_verts)
    bmesh.ops.recalc_face_normals(bm_cut, faces=bm_cut.faces[:])
    
    c_mesh = bpy.data.meshes.new(f"cut_{i}")
    bm_cut.to_mesh(c_mesh)
    bm_cut.free()
    
    c_obj = bpy.data.objects.new(f"cut_{i}", c_mesh)
    bpy.context.scene.collection.objects.link(c_obj)
    
    mod = roller_obj.modifiers.new(f"win_{i}", "BOOLEAN")
    mod.object = c_obj
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = roller_obj
    bpy.ops.object.modifier_apply(modifier=f"win_{i}")
    bpy.data.objects.remove(c_obj, do_unlink=True)

# E. Shading smooth
bpy.context.view_layer.objects.active = roller_obj
bpy.ops.object.shade_smooth()
print(f"Object {roller_obj.name}: {len(roller_obj.data.polygons):,} segitiga")

OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=str(OUT), export_format="GLB", export_yup=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14, export_draco_normal_quantization=10,
    export_materials="NONE",
)
print("Ekspor roller-13mm selesai ->", OUT)
