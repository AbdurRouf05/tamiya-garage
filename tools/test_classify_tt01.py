import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath='d:/coding/game/tamiya-garage/models/source/tamiya-tt01-rc/Tamiya TT-01.stl')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.mesh.separate(type='LOOSE')

parts = sorted(bpy.context.scene.objects, key=lambda o: len(o.data.polygons), reverse=True)

classified = {
    'rims': [],
    'tires': [],
    'sasis': [],
    'drivetrain': [],
    'suspension': [],
    'electronics': [],
    'body_posts': [],
    'unclassified': []
}

for p in parts:
    bb = [list(c) for c in p.bound_box]
    center = [round(sum(c[k] for c in bb)/8.0, 2) for k in range(3)]
    dims = [round(max(c[k] for c in bb) - min(c[k] for c in bb), 2) for k in range(3)]
    min_c = [round(min(c[k] for c in bb), 2) for k in range(3)]
    max_c = [round(max(c[k] for c in bb), 2) for k in range(3)]
    n_poly = len(p.data.polygons)

    # 1. Rims (4 objects, 37836 polys each)
    if n_poly == 37836:
        classified['rims'].append(p)
        continue

    # 2. Tires (4 objects, 6624 polys each)
    if n_poly == 6624:
        classified['tires'].append(p)
        continue

    # 3. Main chassis tub (53423 polys)
    if n_poly == 53423:
        classified['sasis'].append(p)
        continue

    # 4. Long antenna tube or body posts
    if max_c[1] > 20:
        classified['body_posts'].append(p)
        continue
    if dims[1] > 7 and dims[0] < 2 and dims[2] < 2:
        classified['body_posts'].append(p)
        continue

    # 5. Electronics: Battery, ESC, Servo
    if dims[2] > 10 and dims[0] > 3 and abs(center[0]) > 2:
        classified['electronics'].append(p)
        continue
    if abs(center[0] - 3.33) < 1.0 and abs(center[2] - 3.25) < 1.5:
        classified['electronics'].append(p)
        continue
    # Servo: near center=[1.24, 2.84, 7.2] or X near 0-2, Z near 5-8
    if 5.5 < center[2] < 8.5 and abs(center[0]) < 3.5:
        classified['electronics'].append(p)
        continue

    # 6. Drivetrain: Motor, Propeller Shaft, Diff gears
    if abs(center[0] - 2.94) < 1.5 and -11 < center[2] < -3:
        classified['drivetrain'].append(p)
        continue
    if dims[2] > 15 and dims[0] < 2:
        classified['drivetrain'].append(p)
        continue
    if abs(center[0]) < 1.8 and abs(center[1] - 2.3) < 1.0 and (abs(center[2] - 13.95) < 3.0 or abs(center[2] + 13.95) < 3.0):
        classified['drivetrain'].append(p)
        continue

    # 7. Suspension: Springs/dampers, wishbone arms, knuckles
    # Dampers/springs: 4 coilovers, center Z near +/- 15.8, X near +/- 4.0
    if abs(abs(center[2]) - 15.8) < 1.5 and abs(abs(center[0]) - 4.0) < 2.0:
        classified['suspension'].append(p)
        continue
    # Wishbones & knuckles: outer suspension regions (abs(X) > 4.5 and abs(Z) > 10)
    if abs(center[0]) > 4.5 and abs(center[2]) > 9:
        classified['suspension'].append(p)
        continue

    classified['unclassified'].append((p, center, dims, n_poly))

for k in ['rims', 'tires', 'sasis', 'electronics', 'body_posts', 'drivetrain', 'suspension']:
    print(f'{k}: {len(classified[k])} parts, {sum(len(p.data.polygons) for p in classified[k])} polys')

print('Unclassified count:', len(classified['unclassified']))
for p, center, dims, n_poly in classified['unclassified'][:30]:
    print(f'  {p.name}: poly={n_poly}, center={center}, dims={dims}')
