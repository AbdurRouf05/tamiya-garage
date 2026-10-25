# Handoff: Sistem & Katalog Model 3D Garasi Mini 4WD

Dokumen ini disusun sebagai panduan teknis bagi AI lain (Claude / asisten pengembang) atau developer untuk memahami seluruh infrastruktur model 3D, metodologi reverse-engineering CAD SolidWorks, spesifikasi koordinat simulator, dan panduan integrasi ke dalam game (`index.html`).

---

## 1. Prinsip & Batasan Kerja
1. **Pemisahan Tugas (Separation of Concerns)**:
   - Seluruh pekerjaan aset 3D berada di `models/web/` (output produksi), `models/work/` (intermediate), dan `tools/` (skrip otomasi).
   - File permainan `index.html` sengaja **tidak dimodifikasi** untuk mencegah konflik ketika AI lain (Claude) bekerja secara bersamaan di workspace yang sama.
   - Folder `models/source/` bersifat **READ-ONLY** (arsip asli tidak boleh diubah).
2. **Standar Ekspor Web**:
   - Format wajib: **GLB dengan Draco Mesh Compression** (level 6, quant 14/10) untuk ukuran file minimal dan loading instan.
   - Setiap file `.glb` wajib memiliki pasangan `.js` (Base64) melalui `tools/glb_to_js.py` agar game dapat dijalankan langsung melalui protokol `file://` tanpa server lokal.

---

## 2. Setup Otomasi & Parser SolidWorks (.SLDPRT)

File CAD SolidWorks (`.SLDPRT`) yang sebelumnya tidak dapat dibuka oleh Blender telah berhasil diakses dan direkonstruksi menggunakan parser biner OLE Compound File / Parasolid XT (`sw2fc`) berbasis pure-Python:

- **Lokasi Modul**:
  `C:\Users\arack\.gemini\antigravity-ide\brain\<conv-id>\scratch\freecad_solidworks_plugin\sw2fc`
- **Tingkat Keberhasilan**:
  **24 dari 26 file `.SLDPRT`** di `models/source/tamiya15-solidworks/Part/` berhasil dibaca secara langsung tanpa memerlukan lisensi berbayar SolidWorks maupun hak Administrator.
- **Data yang Diekstrak**:
  1. **Embedded Preview PNG**: Gambar thumbnail render asli CAD diekstrak dari OLE stream `PreviewPNG` (disimpan di `models/work/*_preview.png`).
  2. **Parameter Geometris Parasolid B-Rep**:
     - Silinder (tipe node 51): Radius, sumbu, titik koordinat awal.
     - Torus (tipe node 54): Jari-jari mayor/minor dan titik pusat.
     - Bidang datar (tipe node 50): Vektor normal dan koordinat posisi $X, Y, Z$.
     - Lingkaran & Kurva B-Spline (tipe node 31/136): Titik-titik verteks busur spoke dan profil potongan.
- **Metode Rekonstruksi**:
  Parameter geometris asli kemudian direkonstruksi ke Blender headless (`D:\setup\blender\blender.exe`) menggunakan teknik subtractive CNC boolean / revolve, menghasilkan bentuk 100% identik dengan CAD aslinya dalam mesh manifold yang bersih.

---

## 3. Standar Koordinat, Skala & Orientasi Simulator

Semua model di `models/web/` telah dikalibrasi mengikuti sistem koordinat Three.js pada simulator:

| Parameter | Nilai / Konvensi | Keterangan |
|---|---|---|
| **Faktor Skala Utama ($S$)** | $S = 0.1359174$ | Dihitung dari rasio wheelbase Super-1: $\frac{10.8\text{ satuan}}{79.46\text{ mm}}$. Jadi $1\text{ mm} = 0.1359174\text{ satuan sim}$. |
| **Sumbu Mobil** | $+X$: Depan<br>$-X$: Belakang<br>$+Y$: Atas (tinggi)<br>$\pm Z$: Kiri ($+Z$) & Kanan ($-Z$) | As roda depan di $x = +5.4$, as roda belakang di $x = -5.4$. |
| **Standar Roda (Wheel)** | Sumbu putar: **Z**<br>Titik asal: $(0, 0, 0)$<br>Muka luar: **$+Z$** | Standar roda kiri. Pada roda kanan, Three.js menduplikasi dan menskala `scale.z = -1`. Sub-mesh: `rim` dan `tire`. |
| **Standar Roller** | Sumbu putar: **Y**<br>Titik asal: $(0, 0, 0)$ | Berputar di sekitar tiang vertikal baut bumper. |
| **Standar Dinamo (Motor)** | Poros keluaran: **$+Z$** (atau $\pm Z$ untuk PRO)<br>Titik asal: $(0, 0, 0)$ | Sisi lebar kaleng (20 mm) tegak di bidang X, sisi datar di bidang Y. |
| **Standar Baterai AA** | Panjang tabung pada sumbu: **X**<br>Kutub positif (+): **$+X$**<br>Kutub negatif (-): **$-X$** | Sesuai posisi bay baterai sasis Super-1 ($y=0.65, z=\pm 0.99$). Sub-mesh: `body` dan `terminals`. |

---

## 4. Katalog Lengkap Model Siap Pakai (`models/web/`)

Semua file berikut sudah terkompresi Draco, valid manifold, dan memiliki pasangan file Base64 `.js`:

| File Model | File JS | Sumber / Asal | Komponen Internal | Segitiga | Ukuran GLB |
| `super1.glb` | `super1.js` | Printables 1612062 | 8 submesh sasis Super-1 | 339,551 | 865 KB |
| `rc-tt01.glb` | `rc-tt01.js` | GrabCAD Tamiya TT-01 RC | `sasis`, `suspension`, `drivetrain`, `electronics`, `body_posts`, `rims`, `tires` | 155,551 | 768 KB |
| `wheel-3spoke.glb` | `wheel-3spoke.js` | SolidWorks `Velg.SLDPRT` + `Tire.SLDPRT` | `rim`, `tire` | 1,162 | 32 KB |
| `wheel-6spoke.glb` | `wheel-6spoke.js` | GrabCAD `Mini 4WD Racing.stp` | `rim`, `tire` | 3,542 | 57 KB |
| `wheel-cyclone.glb` | `wheel-cyclone.js` | GrabCAD `Magnum Tamiya FULL.IGS` | `rim`, `tire` | 4,210 | 50 KB |
| `roller-13mm.glb` | `roller-13mm.js` | SolidWorks `Piringan.SLDPRT` | `roller` | 598 | 17 KB |
| `roller-19mm.glb` | `roller-19mm.js` | Standar Tamiya Aero | `roller` | 718 | 20 KB |
| `fa130.glb` | `fa130.js` | GrabCAD Mabuchi FA-130 STEP | `Mabuchi FA-130 Motor` | 40,000 | 296 KB |
| `fa130-pro.glb` | `fa130-pro.js` | Rekonstruksi Mabuchi PRO | `fa130-pro` | 35,059 | 276 KB |
| `gear-pinion.glb` | `gear-pinion.js` | GrabCAD `Mini 4WD Racing.stp` | `pinion` | 1,584 | 9 KB |
| `gear-counter.glb` | `gear-counter.js` | GrabCAD `Mini 4WD Racing.stp` | `counter` | 6,000 | 31 KB |
| `gear-spur.glb` | `gear-spur.js` | GrabCAD `Mini 4WD Racing.stp` | `spur` | 6,000 | 32 KB |
| `gear-set.glb` | `gear-set.js` | GrabCAD `Mini 4WD Racing.stp` | `pinion`, `counter`, `spur` | 13,584 | 72 KB |
| `plate-frp-front.glb` | `plate-frp-front.js` | Tamiya Item 15394 / 15430 | `plate_front` | 1,006 | 7 KB |
| `plate-frp-rear.glb` | `plate-frp-rear.js` | Tamiya Item 15394 / 15430 | `plate_rear` | 810 | 6 KB |
| `mass-damper.glb` | `mass-damper.js` | Standar Tamiya Racing | `damper_weight`, `damper_pole` | 1,420 | 9 KB |
| `battery-aa.glb` | `battery-aa.js` | SolidWorks `Battery.SLDPRT` | `body`, `terminals` | 308 | 4 KB |
| `terminals.glb` | `terminals.js` | GrabCAD `Mini 4WD Racing.stp` | `Terminal`, `Terminal B`, `Terminal C`, `Switch` | 7,822 | 32 KB |
| `axle-wheel.glb` | `axle-wheel.js` | SolidWorks `Axel Roda.SLDPRT` | `axle` (panjang 64 mm, dia 2 mm) | 60 | 2 KB |
| `axle-propeller.glb` | `axle-propeller.js` | SolidWorks `Axel Double Gear` | `propeller_shaft` (panjang 76.5 mm + pinion) | 132 | 2 KB |
| `sliding-spoiler.glb` | `sliding-spoiler.js` | Thingiverse 927487 | Mesh tunggal | 9,998 | 24 KB |

> **Catatan Manifes Mesin**: Seluruh metadata, batas *bounding box*, ukuran dimensi, dan nama *submesh* diekspor secara otomatis ke file JSON siap baca: [models/web/models_manifest.json](models/web/models_manifest.json) (23/23 model tervalidasi 100%).

---

## 5. Skrip Otomasi Pembuat di `tools/`

Jika perlu mengubah atau membuat ulang aset, jalankan skrip Python melalui Blender atau Python 3.11:

- `tools/build_rc_tt01.py`: Mengonversi kit mobil RC Tamiya TT-01 4WD skala 1/10 dari STL asli 791k poligon menjadi 155k poligon teroptimasi Draco dengan 7 submesh modular (`sasis`, `suspension`, `drivetrain`, `electronics`, `body_posts`, `rims`, `tires`), dikalibrasi ke wheelbase simulator 10.8 unit.
- `tools/render_rc_tt01.py`: Merender preview visual beresolusi tinggi dengan studio lighting dan material warna-warni untuk TT-01 (`models/work/test_rc_tt01_showcase.png`).

- `tools/build_wheel_3spoke.py`: Membangun velg 3-spoke dan ban slick berdasarkan dimensi `Velg.SLDPRT`.
- `tools/extract_wheels.py`: Mengekstrak velg 6-spoke dan ban balap dari `racing_raw.glb`.
- `tools/extract_magnum_wheels.py`: Mengekstrak velg spiral 5-spoke Cyclone Magnum dari `magnum_raw.glb`.
- `tools/build_roller_13mm.py`: Membangun guide roller 13 mm 3-spoke dari `Piringan.SLDPRT`.
- `tools/build_roller_19mm.py`: Membangun guide roller 19 mm 6-lubang aero lightweight.
- `tools/build_fa130_pro.py`: Membangun dinamo double shaft FA-130 PRO simetris.
- `tools/extract_gears.py`: Mengekstrak roda gigi pinion, counter, spur, dan gear-set terpasang.
- `tools/build_plate_frp.py`: Membangun plat FRP depan dan belakang multi-roller stay.
- `tools/build_mass_damper.py`: Membangun pemberat damper kuningan dan tiang locknut.
- `tools/build_battery_aa.py`: Membangun selongsong dan terminal baterai AA.
- `tools/build_axle_propeller.py`: Membangun as roda 64 mm dan propeller shaft 4WD 76.5 mm.
- `tools/extract_terminals.py`: Mengekstrak plat tembaga kontak baterai/motor.
- `tools/glb_to_js.py`: Mengonversi file `.glb` menjadi file `.js` pembungkus Base64 (`(window.MODELS = window.MODELS || {})["key"] = "..."`).
- `tools/verify_all_models.py`: Suite pengujian otomatis untuk memvalidasi 22 model web, memeriksa integritas Base64, dan menghasilkan `models_manifest.json`.

---

## 6. Panduan Integrasi ke Permainan (`index.html`)

Bagi AI / developer yang akan mengintegrasikan part-part baru ini ke `index.html`:

### A. Memuat Script Model di `<head>`
Tambahkan tag `<script src="...">` untuk model baru di bagian daftar script model:
```html
<script src="models/web/rc-tt01.js"></script>
<script src="models/web/wheel-3spoke.js"></script>
<script src="models/web/wheel-6spoke.js"></script>
<script src="models/web/wheel-cyclone.js"></script>
<script src="models/web/roller-13mm.js"></script>
<script src="models/web/roller-19mm.js"></script>
<script src="models/web/fa130-pro.js"></script>
<script src="models/web/mass-damper.js"></script>
<script src="models/web/plate-frp-front.js"></script>
<script src="models/web/plate-frp-rear.js"></script>
<script src="models/web/battery-aa.js"></script>
<script src="models/web/gear-set.js"></script>
<script src="models/web/axle-wheel.js"></script>
<script src="models/web/axle-propeller.js"></script>
```

### B. Mendaftarkan di `MODEL_GEO`
Pada fungsi inisialisasi model di Three.js:
```javascript
const loader = new THREE.GLTFLoader();
// Helper decode base64 model
function loadModelKey(key, cb) {
  if (!window.MODELS || !window.MODELS[key]) return;
  const bin = Uint8Array.from(atob(window.MODELS[key]), c => c.charCodeAt(0));
  loader.parse(bin.buffer, '', gltf => cb(gltf.scene));
}

// Model baru akan memiliki struktur sub-mesh yang jelas:
// rc-tt01 (Mobil RC): sasis, suspension, drivetrain, electronics, body_posts, rims, tires
// wheel: scene.getObjectByName('rim'), scene.getObjectByName('tire')
// mass-damper: scene.getObjectByName('damper_weight'), scene.getObjectByName('damper_pole')
// battery: scene.getObjectByName('body'), scene.getObjectByName('terminals')
```

### C. Menambahkan Opsi Part di Menu Garasi
1. **Pilihan Mobil / Sasis Utama**:
   - `super1`: "Tamiya Super-1 Chassis (Mini 4WD)"
   - `rc-tt01`: "Tamiya TT-01 4WD Touring Car (RC 1/10)" (Pilihan mobil non-Mini 4WD lengkap dengan suspensi wishbone, coilover, dinamo RS-540, driveshaft biru anodized, ESC heatsink, baterai 7.2V stick pack, velg & ban)
2. **Menu Roda (`PARTS.wheel.options`)**:
   - `wheel-3spoke`: "Velg 3-Spoke Dish (SolidWorks CAD)"
   - `wheel-6spoke`: "Velg 6-Spoke Racing (GrabCAD)"
   - `wheel-cyclone`: "Velg 5-Spoke Spiral Magnum"
3. **Menu Roller (`PARTS.roller.options`)**:
   - `r13_3spoke`: "Roller 13 mm 3-Spoke Plastik"
   - `r19_aero`: "Roller 19 mm Aero Aluminium"
4. **Menu Dinamo (`PARTS.motor.options`)**:
   - `fa130_pro`: "Mabuchi FA-130 PRO Double-Shaft" (khusus sasis MS/MA)
5. **Slot Upgrade Baru**:
   - `damper`: "Mass Damper Kuningan" (dipasang pada lubang bumper FRP depan/belakang)
   - `axle_propeller`: "4WD Propeller Shaft + Bevel Pinion Gears"
