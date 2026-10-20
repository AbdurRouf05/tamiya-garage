export const meta = {
  name: 'super1-fit-audit',
  description: 'Diagnose how each Super-1 part, motor, battery, rollers and bodies truly fit (measured from STL geometry), adversarially verify, and survey assets for complete models',
  phases: [
    { title: 'Diagnose', detail: 'one agent per fit problem + asset survey, measured from geometry' },
    { title: 'Verify', detail: 'independent skeptic re-measures each diagnosis and tries to refute it' },
  ],
}

const S = args.scratch
const CTX = `
PROJECT: D:\\coding\\tamiya-garage (a Three.js mini 4WD simulator, index.html). You MUST NOT modify index.html, models/web/*, or models/source/* (read-only). Write ALL your own scripts, renders and outputs ONLY inside your scratch folder given below. Do not pip-install anything.
TOOLS: Blender 5.0 at D:\\setup\\blender\\blender.exe (run headless: blender --background --factory-startup --python <script.py> -- <args>; STL import op: bpy.ops.wm.stl_import(filepath=...); glTF import: bpy.ops.import_scene.gltf; Workbench renders with orthographic cameras work and are the best way to SEE fits — Read the PNG files you render). Python 3.11 with numpy, scipy, PIL, cascadio (STEP/IGES->GLB). Existing helper scripts you may read/copy (not edit): tools/blender_view_super1.py (side ortho render with 10 mm markers; camera rotation (90°,0,90°) looks along -X with +Z up and screen-right = +Y), tools/body_clearance.py (heightmap clearance test), tools/find_axle_holes.py, tools/blender_probe.py, tools/blender_probe_glb.py, tools/blender_split_probe.py, tools/cad_to_glb.py, tools/blender_magnum.py, tools/blender_convert.py. Binary STL is easy to read with numpy (header 80 bytes, uint32 count, 50-byte records).

SUPER-1 CHASSIS SOURCE (Printables, mm, Z-up): models/source/super1-printables/chassis-super-1*.stl — 8 files: chassis-super-1.stl (main), -gear-cover, -motor-bracket, -rear-bumper, -switch-cover, -switch-on-off, -battery-retainer, -wheel-bearing. Front of car = low Y (switch end, Y≈0); rear = high Y (motor/rear-bumper end). Car centre line X = 39. Bounding boxes (size; centre): chassis (78,121.9,15.3; 39,61,11.8) i.e. z 4.15..19.45; gear-cover (12.7,31.5,15.8; 23.1,89.8,23.0); motor-bracket (36.7,27.2,27.9; 40.5,90.1,18.0); rear-bumper (54.9,42.5,15.5; 38,113.7,13.0); switch-cover (42.7,16.2,16.7; 38,15.4,13.7); switch-on-off (8,6,11.5; 45.6,18.6,10.7); battery-retainer (34.8,8.0,5.5; 38,54.1,16.5); wheel-bearing (1.8,5.9,5.9; 59.7,15.1,15.1).
MEASURED FACT: the axle holes in the chassis side walls are at Y=30 (front) and Y=110 (rear), Z=15.1; side walls around X≈18.3 and X≈59.7. The wheel-bearing STL is NOT placed at its hole (it is laid out for printing) — so other part files may ALSO not be in assembled position. Each separate part must be mated to the chassis by its real mating features (screw holes/bosses, clips, slots, shaft holes), not by its file position.

SIMULATOR MAPPING (car-local units; 1 unit = 7.43 mm; scale s=0.1346): x_sim = -(Y-70)*s (front = +x), y_sim = (Z-15.1)*s + R where R = wheel radius = 1.75 for the default small wheel (axle height), z_sim = -(X-39)*s. So front axle x=+5.38, rear axle x=-5.38. Wheels: centres (±5.4, R, ±4.55), tyre radius 1.75, width 1.45. In the garage the whole car sits 0.3 higher in world space (world = car-local + (0,0.3,0)).
CURRENT SIMULATOR PLACEMENTS (car-local, from a live dump; bounding-box centre / size): Sasis (1.22,1.31,0)/(16.41,2.06,10.50) min y 0.28; Gear Cover (-2.66,2.81,2.15)/(4.24,2.13,1.71); Dudukan Dinamo/motor bracket (-2.70,2.14,-0.21)/(3.67,3.76,4.94); Bumper Belakang (-5.88,1.47,0.13)/(5.72,2.09,7.38); Penutup Saklar (7.35,1.57,0.13)/(2.18,2.25,5.74); Tombol Saklar (6.93,1.16,-0.89)/(0.81,1.55,1.08); Penahan Baterai (2.14,1.94,0.13)/(1.08,0.74,4.68); FA-130 motor (-2.70,2.38,-0.04)/(2.72,2.25,5.21) shaft toward +z, a coloured cap disc at its -z end; gear group (code-made, in plane z=2.35): pinion r=0.45 at motor centre, counter gear r≈0.81 at ((mx-5.4)/2, (my+R)/2+0.25), spur r=1.45 on the rear axle (-5.4,R) — the spur currently sits OUTSIDE (behind) the gear cover; 2×AA batteries r=0.97 len 6.6 at x=2.20, y=0.65, z=±0.99 (bottom reaches y≈-0.32, i.e. BELOW the chassis bottom 0.28); FRP plates + 13 mm rollers: front rollers (9.32,2.15,±4.80), front plate centre (9.47,1.99,0) size (1.60,0.28,10.80); rear rollers (-8.64,2.15,±3.37), rear plate (-8.79,1.99,0) size (1.60,0.28,7.94).
BODIES: (a) Cyclone Magnum body GLB models/web/body-magnum.glb (Draco; Blender can import it), node 'body', already in sim units, origin at axle mid-point and axle height 0, front +x; simulator places it at (0, R+0.1, 0) with scale (1,1,1.12). (b) "Body Sayap" = models/source/ms-body-thingiverse/files/mini_4wd_ms_chassis.stl transformed as in tools/body_clearance.py with lift 0.9 and scale (1.05,1.28,1.12) (i.e. offset y 1.3), rotated 180° about Y, x offset -0.15.
FA-130 motor model: models/web/fa130.glb (sim units, centred, shaft along -z in the file; simulator rotates it 180° about Y). Raw meters version: ${S}\\cad\\fa130_raw.glb. Real FA-130: body 20 mm wide x 15 mm thick x 25 mm long can, shaft Ø2 mm.
USER COMPLAINTS (Indonesian user, screenshots at C:\\Users\\arack\\AppData\\Local\\Temp\\claude\\D--coding-cozy-village\\bb2493d4-aa52-4045-a5e2-0a655a382ec3\\images\\22.webp and 23.webp — Read them): rear bumper not mounted correctly to the chassis; gear cover and gears not mounted correctly; FRP plate — if it only fits by forcing, don't use it; switch cover not mounted correctly; battery seen from below sticks out past the chassis; motor bracket collides with the body; a round thing looks like it floats; check all other sizes so nothing collides or penetrates; small edits to the 3D models are allowed if needed.

REPORTING: every number must come from measurement you actually performed (say how). Give corrections both in STL mm (translation dX,dY,dZ and rotation if any, about which pivot) and in simulator car-local units. Render orthographic evidence images (before/after) and list their paths. If something cannot be determined, say so explicitly instead of guessing.`

const DIAG = {
  type: 'object',
  properties: {
    key: { type: 'string' },
    summary: { type: 'string', description: 'what is wrong and the fix, 3-6 sentences' },
    findings: { type: 'array', items: { type: 'object', properties: {
      item: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' },
      stl_mm: { type: 'string', description: 'exact numbers in STL mm' },
      sim: { type: 'string', description: 'exact numbers in simulator car-local units' },
      confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
    }, required: ['item', 'problem', 'fix', 'confidence'] } },
    model_edits: { type: 'array', items: { type: 'string' }, description: 'any geometry edits recommended, precise' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'paths of renders / outputs' },
    scripts: { type: 'array', items: { type: 'string' }, description: 'paths of scripts written' },
  },
  required: ['key', 'summary', 'findings', 'evidence'],
}
const VERDICT = {
  type: 'object',
  properties: {
    key: { type: 'string' },
    agrees: { type: 'boolean', description: 'true only if every finding survived your independent check' },
    confirmed_items: { type: 'array', items: { type: 'string' } },
    refuted_items: { type: 'array', items: { type: 'object', properties: {
      item: { type: 'string' }, reason: { type: 'string' }, corrected: { type: 'string', description: 'your measured correct numbers, STL mm and sim' },
    }, required: ['item', 'reason', 'corrected'] } },
    notes: { type: 'string' },
    evidence: { type: 'array', items: { type: 'string' } },
  },
  required: ['key', 'agrees', 'confirmed_items', 'refuted_items', 'notes'],
}

const TASKS = [
  { key: 'rear_bumper', title: 'Rear bumper mating',
    prompt: 'Determine exactly how chassis-super-1-rear-bumper.stl mounts to the rear of chassis-super-1.stl (match its screw holes / bosses / tabs to the chassis features). Is its file position the assembled position? If not, compute the correcting transform. Also locate the rear roller mounting holes on the (corrected) rear bumper and the front roller mounting holes on the chassis front bumper, giving exact roller axis positions (STL mm and sim) — these are where rollers must go.' },
  { key: 'gear_train', title: 'Gear cover + gear train',
    prompt: 'Determine how chassis-super-1-gear-cover.stl and chassis-super-1-motor-bracket.stl mate with the chassis (are their file positions assembled positions? correct them if not). Then find, from the geometry, the real gear-train layout of a Super-1: motor shaft axis position (from the motor bracket cavity / shaft hole), the counter-gear shaft hole (in chassis or bracket), the rear axle (Y=110, Z=15.1), and the free space inside the gear cover. Give pinion, counter-gear and spur centres and the maximum radii that fit inside the cover without penetrating it or the chassis, so the code-made gears end up fully inside the gear cover. The spur gear is on the rear axle on the gear-cover side.' },
  { key: 'switch', title: 'Switch cover + knob',
    prompt: 'Determine how chassis-super-1-switch-cover.stl and chassis-super-1-switch-on-off.stl mount to the chassis front (match clips/holes/slots; the knob slides in a slot of the cover). Are the file positions assembled positions? Compute correcting transforms.' },
  { key: 'battery', title: 'Battery bay + retainer',
    prompt: 'Measure the chassis battery bay: floor top Z, side wall inner X limits, front/back terminal-wall Y limits, and any holes in the floor. Place 2×AA cells (Ø14.5 × 50.5 mm, side by side, axes along Y) so they rest on the floor inside the bay without penetrating anything and without protruding below the chassis bottom. Then determine where chassis-super-1-battery-retainer.stl clips on (its correct transform). Give battery cylinder centres/axis/length in STL mm and sim.' },
  { key: 'motor_body', title: 'Motor fit + body collisions',
    prompt: 'Using the (corrected if needed) motor bracket, find the motor cavity and place the FA-130 motor correctly inside it (centre, axis, which side the shaft exits — must be the gear-cover side). Then test collisions between {chassis, gear cover, motor bracket, FA-130, rear bumper, switch cover} and each body (Magnum as placed: offset y R+0.1, scale (1,1,1.12); and Body Sayap as placed) — find every penetration (where, how deep). Propose the smallest body adjustment (lift / scale / local geometry edit such as raising or cutting a region) that removes them while keeping the wheel arches over the wheels and the body sitting on the chassis (body bottom should rest near the chassis, not float). Quantify before/after.' },
  { key: 'front_rollers', title: 'Front rollers, FRP plates, floating disc',
    prompt: 'Find the front bumper geometry of chassis-super-1.stl (roller holes/stays at the front corners). Decide where front rollers must be (axis vertical) so they mount to the bumper and do not touch the tyres (tyres: centres x=±5.4 sim, radius 1.75, width 1.45, z centre ±4.55). Then judge the FRP/carbon plate: can a plate be mounted front/rear without colliding with tyres, body or chassis and without floating? If it only fits by forcing, recommend not using it (state precisely for which ends). Finally identify the "round thing that looks like it floats" in the user screenshots (images 22/23): reason from the current placements above and the screenshots which object it is, and how to fix it.' },
  { key: 'assets', title: 'Asset survey for complete models',
    prompt: 'Survey every model asset in D:\\coding\\tamiya-garage\\models (source/ and archives/, including zips you may extract into YOUR scratch folder only) to find the most complete, detailed mini 4WD model(s) — e.g. models/source/racing-grabcad (Mini 4WD Racing .stp + .stl, a full chassis with wheels/motor/battery), the Magnum IGES (chassis, wheels, rollers groups besides the body; see tools/blender_magnum.py), tamiya15 SolidWorks (not convertible), gearbox, etc. Convert the STEP with cascadio keeping parts separate (cascadio.load(..., merge_primitives=True) gives one primitive per part — inspect node/mesh names, count, sizes in Blender) and report: which parts exist (motor, gears with tooth counts, wheels, tyres, rollers, batteries, terminals, chassis), their dimensions, whether they are mutually aligned (assembled), units, and which could replace the code-made parts (gears, wheels, rollers, batteries) or even provide a complete detailed car. Render a labelled preview of the best candidate(s). Note licence situation (GrabCAD files have no licence file).' },
]

phase('Diagnose')
const results = await pipeline(
  TASKS,
  t => agent(`${CTX}\n\nYOUR SCRATCH FOLDER: ${S}\\wf\\${t.key} (create it).\n\nTASK (${t.title}): ${t.prompt}\n\nReturn key="${t.key}".`,
    { label: `diagnose:${t.key}`, phase: 'Diagnose', schema: DIAG }),
  (d, t) => d && agent(`${CTX}\n\nYOUR SCRATCH FOLDER: ${S}\\wf\\verify_${t.key} (create it).\n\nYou are an independent SKEPTIC. Another agent produced the diagnosis below for task "${t.title}" (${t.prompt}). Do NOT trust its numbers or images. Re-measure every finding yourself with your own method (prefer a different method from theirs: e.g. if they used a heightmap, you use ortho renders + nearest-distance checks; if they used renders, you compute distances/hole alignments numerically), applying their proposed corrections to the STL/GLB geometry and checking that holes line up, nothing penetrates, nothing floats. Try hard to refute each finding; for any finding that is wrong or imprecise, give your own measured correct numbers. For the asset survey, verify the files/parts/dimensions claims actually hold.\n\nDIAGNOSIS TO VERIFY:\n${JSON.stringify(d, null, 2)}\n\nReturn key="${t.key}".`,
    { label: `verify:${t.key}`, phase: 'Verify', schema: VERDICT }).then(v => ({ diagnosis: d, verdict: v })),
)
return results.filter(Boolean)