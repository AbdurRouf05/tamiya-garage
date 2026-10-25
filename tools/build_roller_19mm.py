"""Membuat model 3D presisi Roller 19 mm Aluminium Aero Lightweight.
Standar Tamiya:
- Diameter luar: 19.0 mm (R = 9.5 mm * S)
- Tebal: 2.2 mm
- Alur lingkar luar (outer groove) penahan O-ring karet
- Lubang baut tengah 2.0 mm (R = 1.0 mm * S) dengan boss bantalan 3.0 mm (R = 1.5 mm * S)
- 6 lubang aero bulat (weight-reduction holes) berdiameter 2.8 mm pada radius 5.8 mm
- Sumbu putar Y, terpusat di (0,0,0).
"""
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Matrix, Vector

OUT = Path("models/web/roller-19mm.glb")
S = 0.1359174  # mm -> simulator scale

bpy.ops.wm.read_factory_settings(use_empty=True)

r_out = 9.5 * S       # R = 9.5 mm (diameter 19 mm)
thick = 2.2 * S       # tebal 2.2 mm
r_boss = 1.8 * S      # boss bantalan tengah
r_hole = 1.0 * S      # lubang baut M2
r_holes_circle = 5.8 * S  # radius lingkaran lubang-lubang aero
r_aero_hole = 1.4 * S     # diameter lubang aero 2.8 mm

# A. Cylinder piringan utama (sumbu Y)
bpy.ops.mesh.primitive_cylinder_add(radius=r_out, depth=thick, vertices=48, location=(0, 0, 0))
roller_obj = bpy.context.active_object
roller_obj.name = "roller"
roller_obj.data.name = "roller"
roller_obj.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)

# B. Alur karet luar (groove)
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

# D. 6 Lubang Aero Bulat mengelilingi piringan
for i in range(6):
    ang = i * 2.0 * math.pi / 6.0
    x = r_holes_circle * math.cos(ang)
    z = r_holes_circle * math.sin(ang)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r_aero_hole,
        depth=thick * 3.0,
        vertices=24,
        location=(x, 0, z)
    )
    aero_cyl = bpy.context.active_object
    aero_cyl.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    
    mod = roller_obj.modifiers.new(f"aero_{i}", "BOOLEAN")
    mod.object = aero_cyl
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = roller_obj
    bpy.ops.object.modifier_apply(modifier=f"aero_{i}")
    bpy.data.objects.remove(aero_cyl, do_unlink=True)

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
print("Ekspor roller-19mm selesai ->", OUT)
