"""Konversi Tamiya TT-01 1/10 RC Car kit STL ke Web GLB (Draco) + JS wrapper.

Standar koordinat simulator (glTF Y-Up):
  +X = Depan (Front)
  -X = Belakang (Rear)
  +Y = Atas (Up)
  +Z = Kiri (Left)
  -Z = Kanan (Right)
  As roda depan:    x = +5.40, y = 0.0, z = 0.0
  As roda belakang: x = -5.40, y = 0.0, z = 0.0
  Wheelbase: 10.80 satuan simulator

Sub-mesh yang dihasilkan:
  1. sasis: Bak sasis utama (tub chassis), cover gearbox bawah, bumper, baut sasis
  2. suspension: 4 wishbone (upper/lower), 4 coilover damper, shock tower, knuckle
  3. drivetrain: Dinamo RS-540, propeller shaft tengah, spur gear, diff gear, dogbone
  4. electronics: Baterai 7.2V stick pack, ESC heatsink, servo kemudi, bellcrank, tie rods
  5. body_posts: 4 tiang dudukan body & tabung antena
  6. rims: 4 velg balap 5-spoke
  7. tires: 4 ban karet
"""

import math
import os
import sys
import bmesh
import bpy
from mathutils import Matrix

def build_tt01():
    stl_path = "models/source/tamiya-tt01-rc/Tamiya TT-01.stl"
    out_glb = "models/web/rc-tt01.glb"
    
    if not os.path.exists(stl_path):
        print(f"ERROR: {stl_path} tidak ditemukan!")
        sys.exit(1)
        
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=stl_path)
    
    # Pisahkan loose parts
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')
    
    parts = list(bpy.context.scene.objects)
    print(f"Memproses {len(parts)} komponen loose parts TT-01...")
    
    submesh_groups = {
        'rims': [],
        'tires': [],
        'sasis': [],
        'body_posts': [],
        'electronics': [],
        'drivetrain': [],
        'suspension': []
    }
    
    for p in parts:
        bb = [list(c) for c in p.bound_box]
        center = [round(sum(c[k] for c in bb)/8.0, 3) for k in range(3)]
        dims = [round(max(c[k] for c in bb) - min(c[k] for c in bb), 3) for k in range(3)]
        min_c = [round(min(c[k] for c in bb), 3) for k in range(3)]
        max_c = [round(max(c[k] for c in bb), 3) for k in range(3)]
        n_poly = len(p.data.polygons)
        
        # 1. Rims (4 velg, masing-masing 37,836 poligon)
        if n_poly == 37836:
            submesh_groups['rims'].append(p)
            continue
            
        # 2. Tires (4 ban, masing-masing 6,624 poligon)
        if n_poly == 6624:
            submesh_groups['tires'].append(p)
            continue
            
        # 3. Sasis bak utama (53,423 poligon)
        if n_poly == 53423:
            submesh_groups['sasis'].append(p)
            continue
            
        # 4. Body posts & Antena
        # Antena tube menjulang tinggi (max Y > 20)
        if max_c[1] > 20.0 or (dims[1] > 7.0 and dims[0] < 2.0 and dims[2] < 2.0):
            submesh_groups['body_posts'].append(p)
            continue
            
        # 5. Electronics: Baterai, ESC, Servo
        # Baterai stick pack (panjang Z > 10, X < -1.5)
        if dims[2] > 10.0 and dims[0] > 2.5 and center[0] < -1.5:
            submesh_groups['electronics'].append(p)
            continue
        # Baterai holder post/straps
        if abs(center[0] - 5.6) < 0.5 and 1.5 < center[2] < 5.0:
            submesh_groups['electronics'].append(p)
            continue
        if abs(center[0] - (-3.49)) < 1.0 and abs(center[2]) < 6.0 and dims[1] < 3.0:
            submesh_groups['electronics'].append(p)
            continue
        # ESC heatsink & komponen (X > 1.8, 1.5 < Z < 5.0)
        if 1.5 < center[0] < 5.0 and 1.5 < center[2] < 5.0 and center[1] > 2.0:
            submesh_groups['electronics'].append(p)
            continue
        # Servo kemudi & bellcrank (X sekitar -1 s/d +3, Z antara 6.0 dan 10.5)
        if -3.5 < center[0] < 3.5 and 6.0 <= center[2] <= 10.5 and center[1] > 0.5:
            submesh_groups['electronics'].append(p)
            continue
        # Tie rods kemudi (Z antara 11.0 dan 12.5, Y > 2.0)
        if abs(center[2] - 11.6) < 1.0 and center[1] > 2.2:
            submesh_groups['electronics'].append(p)
            continue
            
        # 6. Drivetrain: Motor 540, Propeller Shaft, Diff gears, Dogbones
        # Motor 540: silinder diameter ~3.5cm, panjang ~5.5cm, X > 1.5, Z < -3.0
        if 1.5 < center[0] < 4.5 and -11.5 < center[2] < -3.0:
            submesh_groups['drivetrain'].append(p)
            continue
        # Propeller shaft tengah: panjang Z > 14, X dekat 0
        if dims[2] > 14.0 and dims[0] < 2.5 and abs(center[0]) < 1.5:
            submesh_groups['drivetrain'].append(p)
            continue
        # Spur gear & Pinion & Drivetrain tengah di X dekat 0, Y dekat 2.3
        if abs(center[0]) < 1.5 and abs(center[1] - 2.3) < 1.2 and (-12.0 < center[2] < -7.0 or 9.0 < center[2] < 12.5):
            submesh_groups['drivetrain'].append(p)
            continue
        # As differential tengah (Z = +/- 13.95, X dekat 0)
        if abs(center[0]) < 1.2 and abs(abs(center[2]) - 13.95) < 1.5:
            submesh_groups['drivetrain'].append(p)
            continue
        # Dogbones (drive shafts ke roda, ramping dims Z ~ 1-1.5, X ~ 3-4, Y ~ 2)
        if 2.0 < abs(center[0]) < 5.5 and abs(abs(center[2]) - 13.95) < 1.0 and abs(center[1] - 2.0) < 0.8:
            submesh_groups['drivetrain'].append(p)
            continue
            
        # 7. Suspension: Wishbones, Shocks/Dampers, Knuckles, Hex Hubs
        # Damper coilovers & springs: Z ~ +/- 15.8, X ~ +/- 4.0
        if abs(abs(center[2]) - 15.8) < 1.8:
            submesh_groups['suspension'].append(p)
            continue
        # Wishbone arms & knuckle uprights: daerah suspensi luar (|Z| > 11.5 dan |X| > 1.5)
        if abs(center[2]) > 11.5:
            submesh_groups['suspension'].append(p)
            continue
            
        # Default sisa: sasis / cover
        submesh_groups['sasis'].append(p)
        
    print("\nHasil klasifikasi:")
    for k, v in submesh_groups.items():
        print(f"  {k:15s}: {len(v):3d} part, {sum(len(p.data.polygons) for p in v):>7,} poligon")
        
    # Parameter Transformasi
    # Wheelbase STL: 27.90 cm (dari -13.95 s/d +13.95)
    # Target wheelbase simulator: 10.80 satuan (dari -5.40 s/d +5.40)
    scale = 10.80 / 27.90  # 0.3870967741935484
    y0 = 2.30  # Ketinggian as roda di STL
    
    # Target poligon per submesh untuk optimasi Draco
    target_polys = {
        'rims': 24000,
        'tires': 8000,
        'sasis': 25000,
        'suspension': 45000,
        'drivetrain': 35000,
        'electronics': 15000,
        'body_posts': 4000
    }
    
    # Matriks transformasi ke Blender native Z-Up:
    # x_blender = scale * z_stl       (+X = Depan)
    # y_blender = scale * x_stl       (+Y = Kanan)
    # z_blender = scale * (y_stl - y0) (+Z = Atas)
    # Saat export_yup=True dieksekusi glTF exporter:
    # x_gltf = x_blender = scale * z_stl       (+X = Depan)
    # y_gltf = z_blender = scale * (y_stl - y0) (+Y = Atas)
    # z_gltf = -y_blender = -scale * x_stl     (+Z = Kiri, -Z = Kanan)
    xf = Matrix([
        [0.0, 0.0, scale, 0.0],
        [scale, 0.0, 0.0, 0.0],
        [0.0, scale, 0.0, -scale * y0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    joined_objects = []
    
    for name, obj_list in submesh_groups.items():
        if not obj_list:
            continue
            
        bpy.ops.object.select_all(action='DESELECT')
        for ob in obj_list:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = obj_list[0]
        bpy.ops.object.join()
        
        joined = bpy.context.view_layer.objects.active
        joined.name = name
        joined.data.name = name
        
        # Bersihkan titik ganda per segitiga STL
        bm = bmesh.new()
        bm.from_mesh(joined.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
        bm.to_mesh(joined.data)
        bm.free()
        
        # Transform ke koordinat simulator
        joined.data.transform(xf)
        
        # Decimate jika melebihi target
        curr_poly = len(joined.data.polygons)
        t_poly = target_polys.get(name, curr_poly)
        if curr_poly > t_poly:
            mod = joined.modifiers.new("dec", "DECIMATE")
            mod.ratio = t_poly / curr_poly
            mod.use_collapse_triangulate = True
            dg = bpy.context.evaluated_depsgraph_get()
            new_me = bpy.data.meshes.new_from_object(joined.evaluated_get(dg))
            joined.modifiers.remove(mod)
            old_me = joined.data
            joined.data = new_me
            bpy.data.meshes.remove(old_me)
            new_me.name = name
            
        # Smooth shading
        try:
            joined.data.shade_smooth()
            joined.data.set_sharp_from_angle(angle=math.radians(32))
        except AttributeError:
            pass
            
        joined_objects.append(joined)
        print(f"Submesh '{name:12s}': {len(joined.data.polygons):>7,} poligon, {len(joined.data.vertices):>7,} verteks")

    # Ekspor ke GLB dengan kompresi Draco
    os.makedirs(os.path.dirname(out_glb), exist_ok=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format="GLB",
        export_yup=True,
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_materials="NONE",
    )
    
    file_size_kb = os.path.getsize(out_glb) / 1024
    total_polys = sum(len(o.data.polygons) for o in joined_objects)
    print(f"\nSukses ekspor {out_glb}: {file_size_kb:.1f} KB, total {total_polys:,} poligon!")
    
    # Render preview visual
    render_preview(joined_objects)

def render_preview(objects):
    preview_path = "d:/coding/game/tamiya-garage/models/work/test_rc_tt01.png"
    
    # Warna material per submesh
    colors = {
        'sasis': (0.10, 0.10, 0.12, 1.0),        # Hitam matte nylon
        'suspension': (0.85, 0.85, 0.90, 1.0),   # Putih/abu terang suspensi
        'drivetrain': (0.1, 0.45, 0.9, 1.0),     # Biru metalik anodized (shaft) / silver
        'electronics': (0.2, 0.6, 0.3, 1.0),     # Hijau baterai / heatsink
        'body_posts': (0.25, 0.25, 0.25, 1.0),   # Hitam tiang body
        'rims': (0.8, 0.8, 0.82, 1.0),           # Silver velg
        'tires': (0.05, 0.05, 0.05, 1.0)         # Karet hitam
    }
    
    for ob in objects:
        mat = bpy.data.materials.new(name=f"mat_{ob.name}")
        mat.diffuse_color = colors.get(ob.name, (0.5, 0.5, 0.5, 1.0))
        ob.data.materials.clear()
        ob.data.materials.append(mat)
        
    # Kamera di Blender native Z-Up:
    # Front = +X, Right = +Y, Up = +Z
    cam_data = bpy.data.cameras.new('Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    
    cam.location = (16.0, -18.0, 12.0)
    ttc = cam.constraints.new(type='TRACK_TO')
    empty = bpy.data.objects.new('Empty', None)
    empty.location = (0.0, 0.0, 0.5)
    bpy.context.scene.collection.objects.link(empty)
    ttc.target = empty
    ttc.track_axis = 'TRACK_NEGATIVE_Z'
    ttc.up_axis = 'UP_Z'
    
    # Sun light
    light_data = bpy.data.lights.new(name='Light', type='SUN')
    light_data.energy = 4.0
    light = bpy.data.objects.new(name='Light', object_data=light_data)
    light.rotation_euler = (math.radians(50), math.radians(-25), math.radians(45))
    bpy.context.scene.collection.objects.link(light)
    
    bpy.context.scene.render.resolution_x = 1000
    bpy.context.scene.render.resolution_y = 700
    bpy.context.scene.render.filepath = preview_path
    bpy.ops.render.render(write_still=True)
    print(f"Render visual disimpan ke: {preview_path}")

if __name__ == "__main__":
    build_tt01()
