"""Cetak ukuran dan posisi tiap STL. Jalankan:
blender --background --factory-startup --python tools/blender_probe.py -- <file.stl>...
"""
import sys
import bpy
from mathutils import Vector

files = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
for f in files:
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=f)
    for ob in set(bpy.data.objects) - before:
        pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        size, mid = mx - mn, (mx + mn) / 2
        print(f"PROBE {ob.name:34s} ukuran=({size.x:7.1f},{size.y:7.1f},{size.z:7.1f}) "
              f"tengah=({mid.x:7.1f},{mid.y:7.1f},{mid.z:7.1f}) min_z={mn.z:6.1f} tris={len(ob.data.polygons)}")
