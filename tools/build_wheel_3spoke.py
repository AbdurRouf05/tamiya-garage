"""Membuat model 3D presisi Roda 3-Spoke (Velg + Ban) berdasarkan CAD Velg.SLDPRT & Tire.SLDPRT.
Metode: Subtractive Cutting presisi dengan Exact Boolean Solver:
1. Ban slick diameter 22 mm, lebar 10 mm dengan fillet rounded corner.
2. Velg diameter 20 mm, lebar 10 mm, lip belakang 21 mm.
3. Boss hub belakang (diameter 6.4 mm, panjang 2.5 mm) menghadap sasis (-Z).
4. Ceruk belakang barrel diameter 17 mm.
5. Lubang as 2.0 mm tembus sepanjang sumbu Z.
6. 3 Window cutout melengkung pada face depan, menyisakan 3 palang spoke aerodinamis
   sesuai data CAD asli (R_hub = 3.5 mm, R_rim = 8.5 mm, sudut spoke 30 deg).
7. Terpusat di (0,0,0), sumbu as pada Z, muka luar menghadap +Z.
"""
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Matrix, Vector

OUT = Path("models/web/wheel-3spoke.glb")
S = 0.1359174  # mm -> simulator scale

bpy.ops.wm.read_factory_settings(use_empty=True)

# ==========================================
# 1. BUAT BAN (TIRE) DENGAN PROFILE REVOLVE
# ==========================================
tire_mesh = bpy.data.meshes.new("tire")
tire_obj = bpy.data.objects.new("tire", tire_mesh)
bpy.context.scene.collection.objects.link(tire_obj)

bm = bmesh.new()
r_out = 11.0 * S    # diameter 22 mm
r_in = 9.85 * S     # pas di barrel velg
width_tire = 10.0 * S
w2 = width_tire / 2.0
corner_r = 0.8 * S

pts = []
for a in range(0, 91, 15):
    rad = math.radians(a)
    pts.append(Vector((r_out - corner_r + math.cos(rad) * corner_r, 0, w2 - corner_r + math.sin(rad) * corner_r)))
for a in range(90, 181, 15):
    rad = math.radians(a)
    pts.append(Vector((r_out - corner_r + math.cos(rad) * corner_r, 0, -w2 + corner_r + math.sin(rad) * corner_r)))
pts.append(Vector((r_in, 0, -w2)))
pts.append(Vector((r_in, 0, w2)))

verts = [bm.verts.new(p) for p in pts]
bm.faces.new(verts)

bmesh.ops.spin(
    bm,
    geom=bm.faces[:] + bm.edges[:] + bm.verts[:],
    axis=Vector((0, 0, 1)),
    cent=Vector((0, 0, 0)),
    angle=2.0 * math.pi,
    steps=48,
    use_merge=True,
    use_duplicate=False,
)
bm.to_mesh(tire_mesh)
bm.free()

# ==========================================
# 2. BUAT VELG (RIM) METODE CNC CUTTING
# ==========================================
r_lip = 10.5 * S       # bibir penahan ban diameter 21 mm
r_rim = 10.0 * S       # diameter luar barrel 20 mm
r_barrel_in = 8.5 * S  # diameter dalam barrel 17 mm
r_hub = 3.5 * S        # diameter hub tengah 7 mm
r_hole = 1.0 * S       # lubang as 2.0 mm
width = 10.0 * S
face_recess = 1.0 * S  # lekukan face depan dari ujung bibir luar
face_thick = 2.2 * S   # tebal palang spoke

# A. Cylinder utama velg
bpy.ops.mesh.primitive_cylinder_add(radius=r_rim, depth=width, vertices=48, location=(0, 0, 0))
rim_obj = bpy.context.active_object
rim_obj.name = "rim"
rim_obj.data.name = "rim"

# B. Flange / lip belakang penahan ban (-Z)
bpy.ops.mesh.primitive_cylinder_add(radius=r_lip, depth=1.0 * S, vertices=48, location=(0, 0, -w2 + 0.5 * S))
lip_obj = bpy.context.active_object
mod = rim_obj.modifiers.new("lip_union", "BOOLEAN")
mod.object = lip_obj
mod.operation = "UNION"
mod.solver = "EXACT"
bpy.context.view_layer.objects.active = rim_obj
bpy.ops.object.modifier_apply(modifier="lip_union")
bpy.data.objects.remove(lip_obj, do_unlink=True)

# C. Boss hub belakang penahan sasis (-Z)
hub_boss_len = 2.5 * S
bpy.ops.mesh.primitive_cylinder_add(
    radius=3.2 * S,
    depth=hub_boss_len,
    vertices=32,
    location=(0, 0, -w2 - hub_boss_len / 2.0)
)
boss_obj = bpy.context.active_object
mod = rim_obj.modifiers.new("boss_union", "BOOLEAN")
mod.object = boss_obj
mod.operation = "UNION"
mod.solver = "EXACT"
bpy.context.view_layer.objects.active = rim_obj
bpy.ops.object.modifier_apply(modifier="boss_union")
bpy.data.objects.remove(boss_obj, do_unlink=True)

# D. Ceruk belakang berongga (-Z)
cavity_depth = width - face_recess - face_thick
bpy.ops.mesh.primitive_cylinder_add(
    radius=r_barrel_in,
    depth=cavity_depth,
    vertices=48,
    location=(0, 0, -w2 + cavity_depth / 2.0)
)
cavity_obj = bpy.context.active_object
mod = rim_obj.modifiers.new("cavity_cut", "BOOLEAN")
mod.object = cavity_obj
mod.operation = "DIFFERENCE"
mod.solver = "EXACT"
bpy.context.view_layer.objects.active = rim_obj
bpy.ops.object.modifier_apply(modifier="cavity_cut")
bpy.data.objects.remove(cavity_obj, do_unlink=True)

# E. Ceruk bibir depan (recess face depan sebesar face_recess)
bpy.ops.mesh.primitive_cylinder_add(
    radius=r_barrel_in,
    depth=face_recess * 2.0,
    vertices=48,
    location=(0, 0, w2)
)
front_recess_obj = bpy.context.active_object
mod = rim_obj.modifiers.new("recess_cut", "BOOLEAN")
mod.object = front_recess_obj
mod.operation = "DIFFERENCE"
mod.solver = "EXACT"
bpy.context.view_layer.objects.active = rim_obj
bpy.ops.object.modifier_apply(modifier="recess_cut")
bpy.data.objects.remove(front_recess_obj, do_unlink=True)

# F. Lubang as 2.0 mm sepanjang seluruh sumbu Z
bpy.ops.mesh.primitive_cylinder_add(radius=r_hole, depth=width + hub_boss_len * 2.0 + 4.0 * S, vertices=24, location=(0, 0, 0))
hole_obj = bpy.context.active_object
mod = rim_obj.modifiers.new("hole_cut", "BOOLEAN")
mod.object = hole_obj
mod.operation = "DIFFERENCE"
mod.solver = "EXACT"
bpy.context.view_layer.objects.active = rim_obj
bpy.ops.object.modifier_apply(modifier="hole_cut")
bpy.data.objects.remove(hole_obj, do_unlink=True)

# G. 3 Window Cutouts melengkung pada face depan
for i in range(3):
    mid_deg = 60 + i * 120
    ang0 = math.radians(mid_deg - 38)
    ang1 = math.radians(mid_deg + 38)
    
    bm_cut = bmesh.new()
    pts_cut = []
    
    r_cut_in = r_hub + 0.3 * S
    r_cut_out = r_barrel_in - 0.2 * S
    
    for step in range(6):
        t = step / 5.0
        a = ang0 + t * (ang1 - ang0)
        pts_cut.append(Vector((r_cut_in * math.cos(a), r_cut_in * math.sin(a), -width)))
    
    for step in range(6):
        t = step / 5.0
        a = ang1 - t * (ang1 - ang0)
        pts_cut.append(Vector((r_cut_out * math.cos(a), r_cut_out * math.sin(a), -width)))
        
    f_cut = bm_cut.faces.new([bm_cut.verts.new(p) for p in pts_cut])
    
    res = bmesh.ops.extrude_face_region(bm_cut, geom=[f_cut])
    top_verts = [v for v in res["geom"] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm_cut, vec=Vector((0, 0, width * 2.5)), verts=top_verts)
    bmesh.ops.recalc_face_normals(bm_cut, faces=bm_cut.faces[:])
    
    c_mesh = bpy.data.meshes.new(f"cut_{i}")
    bm_cut.to_mesh(c_mesh)
    bm_cut.free()
    
    c_obj = bpy.data.objects.new(f"cut_{i}", c_mesh)
    bpy.context.scene.collection.objects.link(c_obj)
    
    mod = rim_obj.modifiers.new(f"win_{i}", "BOOLEAN")
    mod.object = c_obj
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = rim_obj
    bpy.ops.object.modifier_apply(modifier=f"win_{i}")
    bpy.data.objects.remove(c_obj, do_unlink=True)

# H. Haluskan shading
for ob in (rim_obj, tire_obj):
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.shade_smooth()
    print(f"Object {ob.name}: {len(ob.data.polygons):,} segitiga")

OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=str(OUT), export_format="GLB", export_yup=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14, export_draco_normal_quantization=10,
    export_materials="NONE",
)
print("Ekspor wheel-3spoke selesai ->", OUT)
