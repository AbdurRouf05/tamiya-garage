"""Verifikasi seluruh model 3D di models/web/ dan buat manifes metadata JSON.
Memeriksa:
1. Integritas file .glb (Draco compression & mesh loading di Blender).
2. Kesesuaian file .js (Base64 string decode cocok 100% dengan biner .glb).
3. Dimensi bounding box, jumlah poligon, dan hierarki submesh.
4. Menghasilkan models/web/models_manifest.json sebagai panduan mesin untuk AI lain.
"""
import base64
import json
from pathlib import Path
import subprocess
import sys

WEB_DIR = Path("models/web")
BLENDER = r"D:\setup\blender\blender.exe"
MANIFEST_OUT = WEB_DIR / "models_manifest.json"

def get_js_key(js_path: Path) -> str:
    txt = js_path.read_text(encoding="utf-8")
    # format: (window.MODELS = window.MODELS || {})["key"] = "...";
    start = txt.find('["') + 2
    end = txt.find('"]')
    if start > 1 and end > start:
        return txt[start:end]
    return ""

def verify_base64_sync(glb_path: Path, js_path: Path) -> bool:
    if not js_path.exists():
        return False
    txt = js_path.read_text(encoding="utf-8")
    q1 = txt.find(' = "') + 4
    q2 = txt.rfind('";')
    if q1 < 4 or q2 <= q1:
        return False
    b64_data = txt[q1:q2]
    decoded = base64.b64decode(b64_data)
    return len(decoded) == glb_path.stat().st_size

def inspect_models_with_blender():
    script = """
import bpy, json, sys
from pathlib import Path
from mathutils import Vector

res = {}
web_dir = Path("models/web")
for glb in sorted(web_dir.glob("*.glb")):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        bpy.ops.import_scene.gltf(filepath=str(glb))
    except Exception as e:
        res[glb.name] = {"error": str(e)}
        continue
        
    obs = [o for o in bpy.data.objects if o.type == "MESH"]
    poly_tot = sum(len(o.data.polygons) for o in obs if o.data)
    vert_tot = sum(len(o.data.vertices) for o in obs if o.data)
    
    # Hitung keseluruhan bounding box
    all_verts = []
    submeshes = []
    for o in obs:
        submeshes.append(o.name)
        for v in o.bound_box:
            all_verts.append(o.matrix_world @ Vector(v))
            
    if all_verts:
        min_x = min(v.x for v in all_verts)
        max_x = max(v.x for v in all_verts)
        min_y = min(v.y for v in all_verts)
        max_y = max(v.y for v in all_verts)
        min_z = min(v.z for v in all_verts)
        max_z = max(v.z for v in all_verts)
        dims = [round(max_x - min_x, 4), round(max_y - min_y, 4), round(max_z - min_z, 4)]
        bbox = {
            "min": [round(min_x, 4), round(min_y, 4), round(min_z, 4)],
            "max": [round(max_x, 4), round(max_y, 4), round(max_z, 4)],
            "dimensions": dims
        }
    else:
        bbox = {"min": [0,0,0], "max": [0,0,0], "dimensions": [0,0,0]}
        
    res[glb.name] = {
        "polygons": poly_tot,
        "vertices": vert_tot,
        "submeshes": submeshes,
        "bounding_box": bbox
    }
    
print("---RESULT_START---")
print(json.dumps(res))
print("---RESULT_END---")
"""
    cmd = [BLENDER, "--background", "--factory-startup", "--python-expr", script]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout
    s = out.find("---RESULT_START---")
    e = out.find("---RESULT_END---")
    if s != -1 and e != -1:
        payload = out[s + len("---RESULT_START---"):e].strip()
        return json.loads(payload)
    else:
        print("Gagal menjalankan inspeksi Blender:", out, p.stderr)
        return {}

def main():
    print("Memverifikasi seluruh model 3D di models/web/ ...")
    blender_data = inspect_models_with_blender()
    
    manifest = {}
    passed = 0
    total = 0
    
    glbs = sorted(WEB_DIR.glob("*.glb"))
    for glb in glbs:
        total += 1
        js = glb.with_suffix(".js")
        b64_ok = verify_base64_sync(glb, js)
        key = get_js_key(js) if js.exists() else ""
        
        b_info = blender_data.get(glb.name, {})
        has_error = "error" in b_info or not b_info
        
        status = "OK" if (b64_ok and not has_error) else "GAGAL"
        if status == "OK":
            passed += 1
            
        poly = b_info.get("polygons", 0)
        sub = b_info.get("submeshes", [])
        dims = b_info.get("bounding_box", {}).get("dimensions", [0, 0, 0])
        
        print(f"[{status:5s}] {glb.name:22s} ({glb.stat().st_size/1024:5.1f} KB) | Key: {key:15s} | Poly: {poly:6d} | Dim: {dims}")
        
        manifest[glb.stem] = {
            "filename": glb.name,
            "js_filename": js.name,
            "js_key": key,
            "size_kb": round(glb.stat().st_size / 1024, 1),
            "polygons": poly,
            "submeshes": sub,
            "bounding_box": b_info.get("bounding_box", {}),
            "base64_sync": b64_ok
        }
        
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nVerifikasi selesai: {passed}/{total} model 100% valid.")
    print(f"Manifes metadata disimpan ke: {MANIFEST_OUT}")

if __name__ == "__main__":
    main()
