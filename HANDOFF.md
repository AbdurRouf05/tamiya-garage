# Serah-terima: Garasi Mini 4WD (status 20 Okt 2026)

## Ringkas
`index.html` = simulator rakit mini 4WD satu file (Three.js r160 dari CDN). Ada mode Garasi/Studio/Lintasan,
aturan kompatibilitas part, exploded view + rakit manual per part, kemudi WASD + drift di Studio,
balap dengan 4 kamera, UI bisa disembunyikan (tombol ×, menu "UI", tombol H).
Buka dengan klik dua kali, atau `python -m http.server 8765` lalu buka `localhost:8765/?debug`
(`?debug` memunculkan `window.__g` = {THREE, renderer, scene, camera, controls, car, parts}).

## Struktur
- `models/source/*` = file asli (JANGAN diubah). `models/archives/*.zip` = unduhan asli. Katalog dan lisensi: `models/README.md`.
- `models/web/*.glb` + `*.js` (GLB base64 supaya jalan di file://): super1, body-aero, body-magnum, fa130.
- `models/work/` = hasil konversi mentah (magnum_raw.glb, fa130_raw.glb).
- `tools/` = skrip konversi dan ukur. Yang penting: `blender_convert.py` (STL→GLB; mendukung koreksi per part
  `"file|nama|target|dx,dy,dz;rx,ry,rz;px,py,pz"` dalam mm), `cad_to_glb.py` (STEP/IGES, butuh cascadio),
  `blender_magnum.py`, `blender_fa130.py`, `body_clearance.py`, `blender_view_super1.py`, `glb_to_js.py`.
- Blender: `D:\setup\blender\blender.exe --background --factory-startup --python <skrip> -- <arg>`.

## Fakta ukur (wajib dipakai)
- Sasis Super-1 (mm, Z atas): depan = Y kecil. **Lubang as Y=30 (depan) & Y=110 (belakang), Z=15,1**; garis tengah X=39; dinding samping X≈18,3 & 59,7.
- Pemetaan ke simulator (s=0,1346; R = jari-jari roda 1,75): `x=-(Y-70)s`, `y=(Z-15,1)s+R`, `z=-(X-39)s`.
  super1.glb sudah diekspor dengan titik asal (39,70,15,1).
- File bearing Printables TIDAK di posisi rakit (offset 14,9 mm). **Dugaan kuat: semua part pelengkap
  (bumper belakang, gear cover, dudukan dinamo, penutup saklar, tombol, penahan baterai) tergeser bersama
  ±(+1, +14…15, 0) mm terhadap sasis** — pencarian voxel agen menemukan kandidat bumper belakang (0,977, 13,96, 0).
  Semua part pelengkap berpusat X=38, sasis X=39. BELUM diverifikasi per part.

## Masalah terbuka (dari user, belum diperbaiki)
1. Bumper belakang, gear cover + gear, penutup saklar tidak terpasang benar ke sasis → cek dugaan offset di atas
   per part dengan `tools/fit_wip/rear_bumper/check_fit.py dx dy dz` (laporkan overlap mm³ & kontak), lalu
   konversi ulang super1.glb dengan koreksi per part.
2. Gear spur (di as belakang, x −5,4) berada di LUAR gear cover → setelah gear cover benar, letakkan pinion/counter/spur di dalamnya.
3. Baterai mencuat ±4,5 mm di bawah sasis (posisi sekarang = penahan_baterai.min.y − 0,92) → ukur lantai bay baterai, AA Ø14,5×50,5 mm.
4. Dudukan dinamo bertabrakan dengan body → ukur ulang setelah part dipindah (body_clearance.py hanya untuk body sayap).
5. Plate FRP: kalau tidak muat tanpa dipaksa, jangan dipakai.
6. "Bundaran melayang" kemungkinan gear yang mencuat di luar gear cover (lihat no. 2).
7. Survei aset: `models/source/racing-grabcad/Mini 4WD Racing.stp` (model lengkap) belum dikonversi per part.
Skrip kerja agen yang terhenti: `tools/fit_wip/<topik>/` (hasil render/npz besar tidak ikut disalin).

## Cara kerja hemat token (penting, kuota user terbatas)
- Kerjakan SATU masalah per sesi, jangan jalankan workflow/banyak agen paralel (sebelumnya kena batas 5 jam).
- Hindari screenshot berulang; cek dengan angka (`window.__g`, skrip Python) dulu.
- User berbahasa Indonesia.
