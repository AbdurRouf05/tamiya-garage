"""Konversi CAD (STEP/IGES) menjadi GLB mentah dengan OpenCASCADE (paket cascadio).

python tools/cad_to_glb.py <masukan.step|.igs> <keluaran.glb> [toleransi_mm]
Hasilnya masih berat; perkecil lagi dengan tools/blender_convert.py.
"""
import sys
import time
from pathlib import Path

import cascadio

src, out = Path(sys.argv[1]), Path(sys.argv[2])
tol = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05
kind = "iges" if src.suffix.lower() in (".igs", ".iges") else "step"
t0 = time.time()
glb = cascadio.load(src.read_bytes(), file_type=kind, tol_linear=tol, tol_angular=0.35,
                    merge_primitives=True, include_materials=True)
if not glb:
    sys.exit(f"Gagal mengonversi {src}")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(glb)
print(f"{src.name} -> {out} ({len(glb) / 1e6:.1f} MB, {time.time() - t0:.0f} dtk)")
