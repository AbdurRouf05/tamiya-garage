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
| `source/tamiya-tt01-rc` | Mobil RC Tamiya TT-01 4WD (skala 1/10) | STL + STEP + SolidWorks | Tidak ada file lisensi (GrabCAD) | ✅ **Diekstrak & Dikonversi.** Kit RC touring car lengkap: sasis, suspensi wishbone, coilover shock, dinamo 540, propeller shaft, gir diff, baterai 7.2V, velg & ban. Disesuaikan ke standar skala wheelbase simulator. |
| `source/tamiya15-solidworks` | Rakitan lengkap (sasis, body, dinamo, gear, roda, baterai) | SolidWorks (.SLDPRT/.SLDASM) | Tidak ada file lisensi (GrabCAD) | ✅ **Bisa diakses & direkonstruksi.** Parser Python mengekstrak parameter CAD & B-Rep Parasolid asli untuk pembuatan model presisi di Blender |

## Sudah dipasang / siap di simulator (`models/web/`)
| File | Dari | Komponen | Segitiga | Ukuran (GLB) |
|---|---|---|---|---|
| `super1.glb` / `.js` | 8 STL Super-1 | sasis, gear cover, motor bracket, bumper, saklar, penahan baterai, bearing | ±340 ribu | 865 KB (Draco) |
| `rc-tt01.glb` / `.js` | GrabCAD Tamiya TT-01 | Kit RC 1/10: `sasis`, `suspension`, `drivetrain`, `electronics`, `body_posts`, `rims`, `tires` | 155.5 ribu | 768 KB (Draco) |
| `body-aero.glb` / `.js` | Thingiverse 893769 | Body balap bersayap | 38 ribu | 139 KB (Draco) |
| `body-magnum.glb` / `.js` | GrabCAD Cyclone Magnum IGES | Shell, sayap, sirip moncong | 60 ribu | 181 KB (Draco) |
| `sliding-spoiler.glb` / `.js` | Thingiverse 927487 | Sliding spoiler stabilizer | 14 ribu | 24 KB (Draco) |
| `wheel-6spoke.glb` / `.js` | GrabCAD Mini 4WD Racing STP | Roda balap 6-spoke (`rim`, `tire`) | 3.5 ribu | 57 KB (Draco) |
| `wheel-cyclone.glb` / `.js` | GrabCAD Cyclone Magnum IGES | Roda spiral 5-spoke (`rim`, `tire`) | 4.2 ribu | 50 KB (Draco) |
| `wheel-3spoke.glb` / `.js` | SolidWorks `Velg.SLDPRT` + `Tire.SLDPRT` | Roda balap 3-spoke aerodinamis (`rim`, `tire`) | 1.1 ribu | 32 KB (Draco) |
| `roller-13mm.glb` / `.js` | SolidWorks `Piringan.SLDPRT` | Guide roller 13 mm 3-spoke + alur dinding | 598 | 17 KB (Draco) |
| `roller-19mm.glb` / `.js` | Standar Tamiya Aero | Guide roller 19 mm 6-lubang aero aluminium | 718 | 20 KB (Draco) |
| `fa130.glb` / `.js` | GrabCAD Mabuchi FA-130 STEP | Dinamo single-shaft (rear/front motor) | 40 ribu | 296 KB (Draco) |
| `fa130-pro.glb` / `.js` | Mabuchi FA-130 PRO | Dinamo double-shaft simetris (MS/MA mid-ship) | 35 ribu | 270 KB (Draco) |
| `gear-pinion.glb` / `.js` | GrabCAD Mini 4WD Racing STP | Pinion gear 8T kuningan/plastik | 1.6 ribu | 9 KB (Draco) |
| `gear-counter.glb` / `.js` | GrabCAD Mini 4WD Racing STP | Counter gear dua tingkat | 6.0 ribu | 31 KB (Draco) |
| `gear-spur.glb` / `.js` | GrabCAD Mini 4WD Racing STP | Spur gear as roda belakang | 6.0 ribu | 32 KB (Draco) |
| `gear-set.glb` / `.js` | GrabCAD Mini 4WD Racing STP | Set lengkap 3 gear terpasang (meshed) | 13.6 ribu | 72 KB (Draco) |
| `axle-wheel.glb` / `.js` | Standar As Roda Mini 4WD | As roda hex 64 mm baja galvanis (`axle`) | 60 | 1.5 KB (Draco) |
| `axle-propeller.glb` / `.js` | Standar As Propeller Mini 4WD | Poros transmisi 4WD 76.5 mm + 2 pinion bevel | 132 | 2.2 KB (Draco) |
| `mass-damper.glb` / `.js` | Standar Tamiya Racing | Damper pemberat kuningan (`damper_weight`, `damper_pole`) | 664 | 9 KB (Draco) |
| `battery-aa.glb` / `.js` | SolidWorks `Battery.SLDPRT` | Baterai AA (`body`, `terminals`) | 86 | 4 KB (Draco) |
| `plate-frp-front.glb` / `.js` | Standar Tamiya FRP Multi Stay | Bumper plate FRP depan multi-roller | 265 | 7 KB (Draco) |
| `plate-frp-rear.glb` / `.js` | Standar Tamiya FRP Multi Stay | Bumper plate FRP belakang multi-roller | 204 | 6 KB (Draco) |
| `terminals.glb` / `.js` | GrabCAD Mini 4WD Racing STP | Plat tembaga terminal dinamo/baterai + saklar | 7.3 ribu | 33 KB (Draco) |

Magnum diskalakan supaya jarak sumbu rodanya 80 mm (sama dengan Super-1), lalu diputar agar moncongnya menghadap +x.
Dinamo FA-130 dipakai untuk semua dinamo single shaft. Dinamo PRO (double shaft) masih memakai versi kode.

Cara membuat ulang (Blender 5 di `D:\setup\blender`):
```
blender --background --factory-startup --python tools/blender_convert.py -- models/web/super1.glb 0.1359174 "39,68.785,15.095" 90 \
  "<S>/chassis-super-1.stl|sasis|140000" \
  "<S>/chassis-super-1-gear-cover.stl|gear_cover|40000|0.977,13.96,0" \
  "<S>/chassis-super-1-motor-bracket.stl|motor_bracket|40000|0.977,13.96,0" \
  "<S>/chassis-super-1-rear-bumper.stl|rear_bumper|60000|0.977,13.96,0" \
  "<S>/chassis-super-1-switch-cover.stl|switch_cover|40000|0.977,13.96,0" \
  "<S>/chassis-super-1-switch-on-off.stl|switch_knob|12000|0.977,13.96,0" \
  "<S>/chassis-super-1-battery-retainer.stl|battery_retainer|2000|0.977,13.96,2.5" \
  "<S>/chassis-super-1-wheel-bearing.stl|wheel_bearing|6000|0.977,13.96,0"
python tools/glb_to_js.py models/web/super1.glb super1
```
(`<S>` = `models/source/super1-printables`.)
Lubang as sasis Super-1 ada di y = 29,055 dan 108,515 mm, z = 15,095 mm (potongan bidang X lewat dinding samping,
lubang r 2,1 mm + ceruk bearing r 2,95 mm di sisi luar). Jarak sumbu roda 79,46 mm, jadi skala 10,8 / 79,46 = 0,1359174
membuat kedua lubang tepat di x = ±5,4 (as roda simulator). Titik asal (39; 68,785; 15,095) mm = tengah kedua lubang as.

Semua part pelengkap di file Printables (gear cover, dudukan dinamo, bumper belakang, penutup saklar, tombol, penahan
baterai, bearing) berada di satu rangka rakitan yang tergeser **T0 = (+0,977; +13,96; 0) mm** dari sasis: pembuatnya hanya
memindahkan sasis ke titik nol XY. Bukti: lubang sekrup bumper belakang tepat di lubang lantai sasis, bearing tepat di
ceruknya, dan tembusan voxel ke sasis turun dari 383/72/21/42 mm³ menjadi ≤ 4 mm³. Penahan baterai dinaikkan 2,5 mm
lagi supaya talinya bertumpu di atas baterai AA yang duduk di lantai bay (di T0 tali memotong baterai 2,5 mm).
File `.js` adalah GLB dalam base64, supaya `index.html` tetap bisa dibuka langsung tanpa server.

## Kewajiban atribusi
- CC BY / BY-SA / BY-NC mewajibkan nama pembuat dicantumkan. Tampilkan kredit di halaman simulator.
- BY-NC: **tidak boleh** dipakai untuk komersial (dijual atau dipasangi iklan berbayar).
- BY-SA: jika modelnya dimodifikasi lalu dibagikan, hasil modifikasinya harus memakai lisensi yang sama.
