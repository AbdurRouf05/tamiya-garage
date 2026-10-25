import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)

# Import exported GLB
glb_path = 'd:/coding/game/tamiya-garage/models/web/rc-tt01.glb'
bpy.ops.import_scene.gltf(filepath=glb_path)

# Warna material per submesh (Principled BSDF)
colors = {
    'sasis': (0.12, 0.12, 0.13, 1.0, 0.8),        # Hitam matte nylon tub
    'suspension': (0.85, 0.85, 0.88, 1.0, 0.4),   # Putih/abu terang suspensi & springs
    'drivetrain': (0.05, 0.35, 0.9, 1.0, 0.2),    # Biru anodized aluminum propeller shaft / silver motor
    'electronics': (0.1, 0.6, 0.25, 1.0, 0.5),    # Hijau baterai pack / heatsink
    'body_posts': (0.2, 0.2, 0.2, 1.0, 0.7),      # Hitam tiang body
    'rims': (0.8, 0.8, 0.82, 1.0, 0.2),           # Silver velg
    'tires': (0.03, 0.03, 0.03, 1.0, 0.9)         # Karet hitam ban
}

for ob in bpy.context.scene.objects:
    if ob.type != 'MESH':
        continue
    spec = colors.get(ob.name, (0.5, 0.5, 0.5, 1.0, 0.5))
    mat = bpy.data.materials.new(name=f"mat_{ob.name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = spec[:4]
        bsdf.inputs['Roughness'].default_value = spec[4]
        if ob.name in ('drivetrain', 'rims'):
            bsdf.inputs['Metallic'].default_value = 0.8
    ob.data.materials.clear()
    ob.data.materials.append(mat)

# World background
world = bpy.data.worlds.new('StudioWorld')
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.08, 0.08, 0.10, 1.0)
    bg.inputs['Strength'].default_value = 1.0

# Key Sun Light
light_data = bpy.data.lights.new(name='KeyLight', type='SUN')
light_data.energy = 3.5
light = bpy.data.objects.new(name='KeyLight', object_data=light_data)
light.rotation_euler = (math.radians(45), math.radians(25), math.radians(-35))
bpy.context.scene.collection.objects.link(light)

# Fill Sun Light
fill_data = bpy.data.lights.new(name='FillLight', type='SUN')
fill_data.energy = 1.5
fill = bpy.data.objects.new(name='FillLight', object_data=fill_data)
fill.rotation_euler = (math.radians(-30), math.radians(-45), math.radians(60))
bpy.context.scene.collection.objects.link(fill)

# Camera
cam_data = bpy.data.cameras.new('Camera')
cam = bpy.data.objects.new('Camera', cam_data)
bpy.context.scene.collection.objects.link(cam)
bpy.context.scene.camera = cam

# Posisi kamera isometric
cam.location = (14.0, -14.0, 10.0)
ttc = cam.constraints.new(type='TRACK_TO')
empty = bpy.data.objects.new('Empty', None)
empty.location = (0.0, 0.0, 0.5)
bpy.context.scene.collection.objects.link(empty)
ttc.target = empty
ttc.track_axis = 'TRACK_NEGATIVE_Z'
ttc.up_axis = 'UP_Z'

bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 800
out_png = 'd:/coding/game/tamiya-garage/models/work/test_rc_tt01.png'
bpy.context.scene.render.filepath = out_png
bpy.ops.render.render(write_still=True)
print('Render preview saved to:', out_png)
