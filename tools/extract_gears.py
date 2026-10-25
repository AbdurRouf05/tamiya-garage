"""Ekstrak roda gigi CAD presisi dari racing_raw.glb (dari Mini 4WD Racing.stp).
Mengekstrak:
1. models/web/gear-pinion.glb (Roda gigi pinion 8T kuningan/plastik pada poros dinamo)
2. models/web/gear-counter.glb (Roda gigi counter dua tingkat)
3. models/web/gear-spur.glb (Roda gigi spur pada poros roda belakang)
4. models/web/gear-set.glb (Ketiga roda gigi dalam konfigurasi terpasang / meshed)

Skala: 1000 * S (S = 0.1359174, rp = 0.272 sesuai simulator Three.js).
"""
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

RAW = Path("models/work/racing_raw.glb")
S = 0.1359174
SCALE = 1000.0 * S

def export_gear(name, target_obj_name, out_path, center=True):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(RAW))
    
    ob = bpy.data.objects.get(target_obj_name)
    if not ob:
        raise ValueError(f"Objek {target_obj_name} tidak ditemukan")
        
    # Hapus semua objek lain
    for o in list(bpy.data.objects):
        if o != ob:
            bpy.data.objects.remove(o, do_unlink=True)
            
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    
    # Skala meter -> mm -> simulator scale
    ob.matrix_world = Matrix.Scale(SCALE, 4) @ ob.matrix_world
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    if center:
        # Pusatkan di (0,0,0)
        bbox = [Vector(b) for b in ob.bound_box]
        mid = sum(bbox, Vector()) / 8.0
        ob.location -= mid
        bpy.ops.object.transform_apply(location=True)
        
    ob.name = name
    if ob.data:
        ob.data.name = name
        # Decimate ringan jika perlu untuk menjaga performa
        n0 = len(ob.data.polygons)
        if n0 > 8000:
            mod = ob.modifiers.new("dec", "DECIMATE")
            mod.ratio = 6000 / n0
            bpy.ops.object.modifier_apply(modifier="dec")
        try:
            ob.data.shade_smooth()
            ob.data.set_sharp_from_angle(angle=math.radians(35))
        except AttributeError:
            pass
            
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out_path), export_format="GLB", export_yup=True, export_apply=True,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_materials="NONE",
    )
    print(f"Ekspor {name} -> {out_path} ({len(ob.data.polygons)} segitiga)")

def export_gear_set(out_path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(RAW))
    
    targets = {
        "Gear 1:1": "pinion",
        "Gear 2:1": "counter",
        "Gear 3:1": "spur"
    }
    
    keep_obs = []
    for raw_name, new_name in targets.items():
        ob = bpy.data.objects.get(raw_name)
        if ob:
            ob.name = new_name
            ob.data.name = new_name
            keep_obs.append(ob)
            
    for o in list(bpy.data.objects):
        if o not in keep_obs:
            bpy.data.objects.remove(o, do_unlink=True)
            
    for ob in keep_obs:
        ob.matrix_world = Matrix.Scale(SCALE, 4) @ ob.matrix_world
        
    # Hitung pusat bersama gearbox
    all_mid = sum((sum([Vector(b) for b in o.bound_box], Vector()) / 8.0 for o in keep_obs), Vector()) / len(keep_obs)
    for ob in keep_obs:
        ob.location -= all_mid
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        if len(ob.data.polygons) > 8000:
            mod = ob.modifiers.new("dec", "DECIMATE")
            mod.ratio = 6000 / len(ob.data.polygons)
            bpy.ops.object.modifier_apply(modifier="dec")
        try:
            ob.data.shade_smooth()
            ob.data.set_sharp_from_angle(angle=math.radians(35))
        except AttributeError:
            pass
            
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out_path), export_format="GLB", export_yup=True, export_apply=True,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_materials="NONE",
    )
    print(f"Ekspor gear-set -> {out_path} ({sum(len(o.data.polygons) for o in keep_obs)} segitiga)")

export_gear("pinion", "Gear 1:1", Path("models/web/gear-pinion.glb"), center=True)
export_gear("counter", "Gear 2:1", Path("models/web/gear-counter.glb"), center=True)
export_gear("spur", "Gear 3:1", Path("models/web/gear-spur.glb"), center=True)
export_gear_set(Path("models/web/gear-set.glb"))
