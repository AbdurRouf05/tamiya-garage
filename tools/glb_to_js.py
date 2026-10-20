"""Bungkus GLB menjadi file JS (base64) supaya index.html bisa dibuka langsung tanpa server.
Browser memblokir fetch() dari file://, tapi <script src> tetap jalan.

python tools/glb_to_js.py models/web/super1.glb super1   ->  models/web/super1.js
"""
import base64
import sys
from pathlib import Path

glb, key = Path(sys.argv[1]), sys.argv[2]
data = base64.b64encode(glb.read_bytes()).decode()
out = glb.with_suffix(".js")
out.write_text(f'(window.MODELS = window.MODELS || {{}})["{key}"] = "{data}";\n')
print(out, f"{out.stat().st_size / 1024:.0f} KB")
