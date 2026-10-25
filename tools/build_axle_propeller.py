"""Membuat model 3D presisi As Roda (Wheel Axle) dan Propeller Shaft 4WD berdasarkan CAD SolidWorks.
1. models/web/axle-wheel.glb:
   - As roda baja hexagonal/silinder diameter 2.0 mm, panjang 64.0 mm
   - Terpusat di (0,0,0), searah sumbu Z (sumbu as roda).
2. models/web/axle-propeller.glb:
   - Poros baling-baling penggerak 4WD (propeller shaft) kawat baja diameter 1.0 mm, panjang 76.5 mm
   - Dilengkapi roda gigi bevel pinion kecil di kedua ujungnya
   - Searah sumbu X (sepanjang mobil depan-belakang).
"""
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

S = 0.1359174  # mm -> simulator scale

def build_wheel_axle():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    out = Path("models/web/axle-wheel.glb")
    
    r_axle = 1.0 * S      # diameter 2.0 mm
    length = 64.0 * S     # panjang 64.0 mm
    
    # As roda sepanjang sumbu Z
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r_axle,
        depth=length,
        vertices=16,
        location=(0, 0, 0)
    )
    ob = bpy.context.active_object
    ob.name = "axle"
    ob.data.name = "axle"
    
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.shade_smooth()
    
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out), export_format="GLB", export_yup=True, export_apply=True,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_materials="NONE",
    )
    print("Ekspor axle-wheel selesai ->", out)

def build_propeller_shaft():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    out = Path("models/web/axle-propeller.glb")
    
    r_wire = 0.5 * S       # kawat baja diameter 1.0 mm
    length = 76.5 * S      # panjang 76.5 mm
    r_pinion = 1.8 * S     # bevel pinion kecil di ujung
    len_pinion = 3.0 * S
    
    # Kawat utama sepanjang sumbu X
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r_wire,
        depth=length,
        vertices=12,
        location=(0, 0, 0)
    )
    wire = bpy.context.active_object
    wire.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    
    # Pinion depan di +X
    bpy.ops.mesh.primitive_cone_add(
        radius1=r_pinion,
        radius2=r_wire,
        depth=len_pinion,
        vertices=12,
        location=(length / 2.0 - len_pinion / 2.0, 0, 0)
    )
    pin_front = bpy.context.active_object
    pin_front.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    
    # Pinion belakang di -X
    bpy.ops.mesh.primitive_cone_add(
        radius1=r_pinion,
        radius2=r_wire,
        depth=len_pinion,
        vertices=12,
        location=(-length / 2.0 + len_pinion / 2.0, 0, 0)
    )
    pin_rear = bpy.context.active_object
    pin_rear.rotation_euler = (0, -math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    
    bpy.context.view_layer.objects.active = wire
    wire.select_set(True)
    pin_front.select_set(True)
    pin_rear.select_set(True)
    bpy.ops.object.join()
    wire.name = "propeller_shaft"
    wire.data.name = "propeller_shaft"
    
    bpy.ops.object.shade_smooth()
    
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out), export_format="GLB", export_yup=True, export_apply=True,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_materials="NONE",
    )
    print("Ekspor axle-propeller selesai ->", out)

build_wheel_axle()
build_propeller_shaft()
