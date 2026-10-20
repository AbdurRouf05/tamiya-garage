# Katalog model 3D

File sumber disimpan di `source/`, zip aslinya di `archives/`. Semua file sumber terlalu berat untuk browser.
Sebelum dipakai di `index.html`, file harus diperkecil dulu lewat Blender menjadi GLB, dan hasilnya disimpan di `models/web/`.

| Folder | Isi | Format | Lisensi | Bisa dipakai? |
|---|---|---|---|---|
| `source/super1-printables` | Sasis Super-1 dalam 8 part terpisah: sasis, gear cover, motor bracket, rear bumper, switch cover, saklar, battery retainer, wheel bearing | STL | CC BY-NC 4.0, karya **reyza hadi** (Printables 1612062) | ✅ **Ya, utama.** Cocok untuk exploded view. Total ±11,6 juta segitiga, jadi wajib diperkecil (gear cover saja 5,7 juta) |
| `source/ms-body-thingiverse` | **Body** mobil balap bersayap. Namanya "MS chassis", tapi isinya body | STL | CC BY-SA, karya **ckw8217** (Thingiverse 893769) | ✅ **Ya.** Ringan (38 ribu segitiga) dan bisa langsung dipakai |
| `source/sliding-spoiler-thingiverse` | Sliding spoiler untuk roller 10 mm | STL | CC BY, karya **Zinzo86** (Thingiverse 927487) | ✅ Ya, sebagai part tambahan |
| `source/racing-grabcad` | Mini 4WD Racing: sasis lengkap dengan roda, dinamo, dan baterai | STL + STEP | Tidak ada file lisensi (GrabCAD) | ⚠️ Hanya untuk belajar pribadi. STL-nya satu kesatuan, jadi part harus dipisah manual di Blender |
| `source/cyclone-magnum-grabcad` | **Cyclone Magnum lengkap**: body, sayap, roda, sekrup | IGES + SolidWorks | Tidak ada file lisensi (GrabCAD) | ⭐ **Sangat cocok** sebagai body utama. Perlu dikonversi dari IGES (format CAD) ke mesh dulu. Hanya untuk pemakaian pribadi atau non-komersial |
| `source/fa130-motor-grabcad` | Dinamo Mabuchi FA-130 (jenis dinamo mini 4WD), lengkap dengan isi dalamnya | STEP + SolidWorks | Tidak ada file lisensi (GrabCAD) | ⭐ **Cocok** untuk menggantikan dinamo versi kode. Perlu konversi STEP. Pribadi/non-komersial |
| `source/gearbox-70093-grabcad` | Tamiya 70093 3-speed crank axle gearbox (kit edukasi) | STEP + Fusion 360 | Tidak ada file lisensi (GrabCAD) | ⚠️ Bukan part mini 4WD. Hanya referensi bentuk gear |
| `archives/tamiya-tt-01-kit-rc-car.zip` | Mobil RC Tamiya TT-01 (skala 1/10) | STL | Tidak ada file lisensi | ❌ Bukan mini 4WD (beda skala dan jenis), tidak diekstrak |
| `source/tamiya15-solidworks` | Rakitan lengkap (sasis, body, dinamo, gear, roda, baterai) | SolidWorks (.SLDPRT/.SLDASM) | Tidak ada file lisensi (GrabCAD) | ❌ Belum bisa. Blender tidak bisa membuka format SolidWorks, jadi harus diekspor ke STEP/STL dulu dari SolidWorks |

## Sudah dipasang di simulator (`models/web/`)
| File | Dari | Segitiga | Ukuran |
|---|---|---|---|
| `super1.glb` / `super1.js` | 8 STL Super-1 (±11,6 juta segitiga, 550 MB) | ±340 ribu | 865 KB (Draco) |
| `body-aero.glb` / `body-aero.js` | body ckw8217 | 38 ribu | 139 KB (Draco) |
| `body-magnum.glb` / `body-magnum.js` | Cyclone Magnum IGES → `tools/cad_to_glb.py` (cascadio) → `tools/blender_magnum.py` (hanya kelompok body: shell, sayap, sirip) | 60 ribu | 242 KB (Draco) |
| `fa130.glb` / `fa130.js` | Mabuchi FA-130 STEP → `tools/cad_to_glb.py` → `tools/blender_fa130.py` | 40 ribu | 395 KB (Draco) |

Magnum diskalakan supaya jarak sumbu rodanya 80 mm (sama dengan Super-1), lalu diputar agar moncongnya menghadap +x.
Dinamo FA-130 dipakai untuk semua dinamo single shaft. Dinamo PRO (double shaft) masih memakai versi kode.

Cara membuat ulang (Blender 5 di `D:\setup\blender`):
```
blender --background --factory-startup --python tools/blender_convert.py -- models/web/super1.glb 0.1346 "39,70,15.1" 90 "<stl>|<nama>|<target>" ...
python tools/glb_to_js.py models/web/super1.glb super1
```
Skala 0,1346 berarti 1 satuan simulator ≈ 7,4 mm (jarak sumbu roda 80 mm = 10,8 satuan).
Titik asal (39, 70, 15,1) mm adalah tengah kedua lubang as. Lubang as sasis Super-1 ada di y = 30 dan 110 mm, z = 15,1 mm
(diukur dari render samping `tools/blender_view_super1.py`). File bearing Printables **tidak** berada di lubangnya
(diletakkan untuk dicetak), jadi simulator memindahkannya ke lubang as.
File `.js` adalah GLB dalam base64, supaya `index.html` tetap bisa dibuka langsung tanpa server.

## Kewajiban atribusi
- CC BY / BY-SA / BY-NC mewajibkan nama pembuat dicantumkan. Tampilkan kredit di halaman simulator.
- BY-NC: **tidak boleh** dipakai untuk komersial (dijual atau dipasangi iklan berbayar).
- BY-SA: jika modelnya dimodifikasi lalu dibagikan, hasil modifikasinya harus memakai lisensi yang sama.
