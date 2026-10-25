"""Membuat model 3D presisi Bumper / Plat FRP Multi-Roller Setting Stay (Depan & Belakang).
Berdasarkan spesifikasi resmi Tamiya FRP Multi Roller Setting Stay (Item 15394 / 15430):
- Lebar total: 103.5 mm (memenuhi regulasi Mini 4WD max 105 mm)
- Ketebalan: 1.5 mm (bahan fiberglass FRP hitam/abu-abu)
- Lubang-lubang presisi:
  - Lubang dudukan tengah (chassis mount holes) berjarak 20 mm dan 26 mm
  - Lubang roller multi-posisi untuk roller 9 mm, 13 mm, dan 19 mm
- Terpusat di (0,0,0), bidang datar XZ, ketebalan pada sumbu vertikal Y.
"""
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Matrix, Vector

OUT_FRONT = Path("models/web/plate-frp-front.glb")
OUT_REAR = Path("models/web/plate-frp-rear.glb")
S = 0.1359174  # mm -> simulator scale

def build_frp_front():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    thick = 1.5 * S
    y2 = thick / 2.0
    
    # 1. Base 2D outline FRP depan (bentuk busur aero melengkung ke depan)
    # Lebar X: -51.5 mm .. +51.5 mm, Kedalaman Z: -6.0 mm .. +7.0 mm
    bm = bmesh.new()
    
    w_half = 51.5 * S
    pts = []
    
    # Sisi kanan ke kiri (busur depan)
    steps = 24
    for i in range(steps + 1):
        t = i / steps
        x = -w_half + t * (2.0 * w_half)
        # Kurva lengkung lembut ke depan di tengah
        z_front = 5.0 * S * math.cos(x / w_half * math.pi * 0.45) + 1.5 * S
        pts.append(Vector((x, -y2, z_front)))
        
    # Ujung kanan melengkung ke belakang
    pts.append(Vector((w_half, -y2, -3.5 * S)))
    pts.append(Vector((w_half - 4.0 * S, -y2, -6.0 * S)))
    
    # Sisi belakang menuju tengah
    for i in range(steps, -1, -1):
        t = i / steps
        x = -w_half + t * (2.0 * w_half)
        z_rear = 3.0 * S * math.cos(x / w_half * math.pi * 0.45) - 4.5 * S
        pts.append(Vector((x, -y2, z_rear)))
        
    pts.append(Vector((-w_half + 4.0 * S, -y2, -6.0 * S)))
    pts.append(Vector((-w_half, -y2, -3.5 * S)))
    
    # Buat face dasar
    f_base = bm.faces.new([bm.verts.new(p) for p in pts])
    
    # Ekstrusi sepanjang sumbu Y setebal thick
    res = bmesh.ops.extrude_face_region(bm, geom=[f_base])
    top_verts = [v for v in res["geom"] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=Vector((0, thick, 0)), verts=top_verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    
    plate_mesh = bpy.data.meshes.new("plate_front")
    bm.to_mesh(plate_mesh)
    bm.free()
    
    plate_obj = bpy.data.objects.new("plate_front", plate_mesh)
    bpy.context.scene.collection.objects.link(plate_obj)
    
    # 2. Potong lubang-lubang pemasangan (mounting holes)
    # Lubang tengah baut sasis (X = +-10 mm, +-13 mm, +-18 mm)
    # Lubang roller (X = +-41 mm [19mm], +-44 mm [13mm], +-48 mm [9mm])
    holes_x = [
        # Tengah (chassis mount)
        -13.0 * S, -10.0 * S, 0.0, 10.0 * S, 13.0 * S,
        # Sayap kiri & kanan (roller mounts)
        -48.0 * S, -44.0 * S, -41.0 * S, -35.0 * S,
        35.0 * S, 41.0 * S, 44.0 * S, 48.0 * S
    ]
    
    r_hole = 1.0 * S  # M2 screw (diameter 2.0 mm)
    
    for i, hx in enumerate(holes_x):
        # Hitung posisi Z yang sesuai lengkungan plat di titik X ini
        z_center = 4.0 * S * math.cos(hx / w_half * math.pi * 0.45) - 1.5 * S
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r_hole,
            depth=thick * 3.0,
            vertices=16,
            location=(hx, 0, z_center)
        )
        cyl_hole = bpy.context.active_object
        
        mod = plate_obj.modifiers.new(f"h_{i}", "BOOLEAN")
        mod.object = cyl_hole
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        bpy.context.view_layer.objects.active = plate_obj
        bpy.ops.object.modifier_apply(modifier=f"h_{i}")
        bpy.data.objects.remove(cyl_hole, do_unlink=True)
        
    bpy.context.view_layer.objects.active = plate_obj
    bpy.ops.object.shade_smooth()
    print(f"Plate Front: {len(plate_obj.data.polygons)} segitiga")
    
    OUT_FRONT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(OUT_FRONT), export_format="GLB", export_yup=True, export_apply=True,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_materials="NONE",
    )
    print("Ekspor plate-frp-front selesai ->", OUT_FRONT)

def build_frp_rear():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    thick = 1.5 * S
    y2 = thick / 2.0
    
    # 2. Base 2D outline FRP belakang (lurus di tengah, sayap melebar di samping)
    bm = bmesh.new()
    w_half = 52.0 * S
    
    pts = [
        Vector((-w_half, -y2, 5.0 * S)),
        Vector((-w_half + 8.0 * S, -y2, 7.5 * S)),
        Vector((-20.0 * S, -y2, 4.0 * S)),
        Vector((20.0 * S, -y2, 4.0 * S)),
        Vector((w_half - 8.0 * S, -y2, 7.5 * S)),
        Vector((w_half, -y2, 5.0 * S)),
        Vector((w_half, -y2, -4.0 * S)),
        Vector((w_half - 6.0 * S, -y2, -6.5 * S)),
        Vector((20.0 * S, -y2, -3.5 * S)),
        Vector((-20.0 * S, -y2, -3.5 * S)),
        Vector((-w_half + 6.0 * S, -y2, -6.5 * S)),
        Vector((-w_half, -y2, -4.0 * S)),
    ]
    
    f_base = bm.faces.new([bm.verts.new(p) for p in pts])
    
    res = bmesh.ops.extrude_face_region(bm, geom=[f_base])
    top_verts = [v for v in res["geom"] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=Vector((0, thick, 0)), verts=top_verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    
    plate_mesh = bpy.data.meshes.new("plate_rear")
    bm.to_mesh(plate_mesh)
    bm.free()
    
    plate_obj = bpy.data.objects.new("plate_rear", plate_mesh)
    bpy.context.scene.collection.objects.link(plate_obj)
    
    # Lubang-lubang baut belakang (chassis mount + roller multi mount)
    holes_data = [
        (-14.0 * S, 0.0), (-10.0 * S, 0.0), (10.0 * S, 0.0), (14.0 * S, 0.0),
        (-48.0 * S, 2.0 * S), (-44.0 * S, 1.0 * S), (-40.0 * S, 0.0),
        (40.0 * S, 0.0), (44.0 * S, 1.0 * S), (48.0 * S, 2.0 * S),
        (-46.0 * S, -2.5 * S), (46.0 * S, -2.5 * S)
    ]
    
    r_hole = 1.0 * S
    for i, (hx, hz) in enumerate(holes_data):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r_hole,
            depth=thick * 3.0,
            vertices=16,
            location=(hx, 0, hz)
        )
        cyl_hole = bpy.context.active_object
        
        mod = plate_obj.modifiers.new(f"h_{i}", "BOOLEAN")
        mod.object = cyl_hole
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        bpy.context.view_layer.objects.active = plate_obj
        bpy.ops.object.modifier_apply(modifier=f"h_{i}")
        bpy.data.objects.remove(cyl_hole, do_unlink=True)
        
    bpy.context.view_layer.objects.active = plate_obj
    bpy.ops.object.shade_smooth()
    print(f"Plate Rear: {len(plate_obj.data.polygons)} segitiga")
    
    OUT_REAR.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(OUT_REAR), export_format="GLB", export_yup=True, export_apply=True,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_materials="NONE",
    )
    print("Ekspor plate-frp-rear selesai ->", OUT_REAR)

build_frp_front()
build_frp_rear()
