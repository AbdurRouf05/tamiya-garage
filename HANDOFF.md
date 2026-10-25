# Serah-terima: Garasi Mini 4WD (status 24 Okt 2026)

## Ringkas
`index.html` = simulator rakit mini 4WD satu file (Three.js r160 dari CDN). Ada mode Garasi/Studio/Lintasan,
aturan kompatibilitas part, exploded view + rakit manual per part, kemudi WASD + drift di Studio,
balap dengan 4 kamera, UI bisa disembunyikan (tombol ×, menu "UI", tombol H).
Buka dengan klik dua kali, atau `python -m http.server 8765` lalu buka `localhost:8765/?debug`
(`?debug` memunculkan `window.__g` = {THREE, renderer, scene, camera, controls, car, parts}).

## Struktur
- `models/source/*` = file asli (JANGAN diubah). `models/archives/*.zip` = unduhan asli. Katalog, lisensi, dan perintah
  konversi ulang super1.glb: `models/README.md`.
- `models/web/*.glb` + `*.js` (GLB base64 supaya jalan di file://): super1, body-aero, body-magnum, fa130.
- `models/work/` = hasil konversi mentah (magnum_raw.glb, fa130_raw.glb).
- `tools/` = skrip konversi dan ukur. Yang penting: `blender_convert.py` (STL→GLB; koreksi per part
  `"file|nama|target|dx,dy,dz;rx,ry,rz;px,py,pz"` dalam mm), `cad_to_glb.py`, `blender_magnum.py`, `blender_fa130.py`,
  `body_clearance.py` (body sayap vs part, sudah memakai pemetaan + titik pasang baru), `glb_to_js.py`.
- `tools/fit_wip/rear_bumper/`: `stlio.py` (baca STL + cache .npy di `cache/`, di-ignore git), `slicer.py` (potongan bidang,
  lingkaran), `voxel.py`, `check_fit.py [part] dx dy dz [h] [lawan]` (overlap/kontak part vs sasis atau part lain).
  `tools/fit_wip/assembly/`: `fit_all.py` (uji T0 + pencarian FFT semua part), `gear_free.py` (ruang bebas tiap poros gear).
  Skrip lama di `tools/fit_wip/<topik>/` lain masih memakai path `D:\coding\tamiya-garage` dan pemetaan lama.
- Blender: `D:\setup\blender\blender.exe --background --factory-startup --python <skrip> -- <arg>`.

## Fakta ukur (wajib dipakai; diukur ulang 24 Okt, fakta lama Y=30/110 SALAH)
- Sasis Super-1 (mm, Z atas): depan = Y kecil. **Lubang as Y=29,055 (depan) & Y=108,515 (belakang), Z=15,095**
  (lubang r 2,1 di dinding X≈18,3–19,3 & 58,8–59,7; ceruk bearing r 2,95 di sisi luar). Jarak sumbu 79,46 mm. Garis tengah X=39.
- Pemetaan ke simulator: s = 10,8/79,46 = 0,135917, R = jari-jari roda: `x=-(Y-68,785)s`, `y=(Z-15,095)s+R`, `z=-(X-39)s`.
  super1.glb diekspor dengan titik asal (39; 68,785; 15,095), jadi kedua lubang as tepat di x=±5,4 (as roda).
- **Semua part pelengkap STL berada di rangka rakitan yang tergeser T0 = (+0,977; +13,96; 0) mm dari sasis** (pembuatnya
  hanya memindahkan sasis ke titik nol XY). Bukti: lubang sekrup bumper (41,41; 97,87)+T0 = lubang lantai sasis (42,39; 111,83);
  bearing Ø5,9 + T0 tepat di ceruknya; overlap voxel ke sasis turun 383/72/21/42/6 → ≤ 4 mm³ (bumper/dudukan/penutup
  saklar/tombol/penahan); pencarian FFT ±2,5 mm memilih tepat T0 untuk gear cover dan bearing. Sisa overlap kecil ada di klip.
- Titik pasang (mm, sesudah T0):
  - Sumbu dinamo (Y 100,32; Z 17,69), cincin dudukan r dalam 10,05. Muka dalam dinding dudukan sisi gear X 32,357
    (lubang bushing Z 14,5–21). Kaleng berdiri: sisi 20 mm tegak, sisi datar menghadap depan/belakang, nyaris menyentuh as.
  - Poros counter Ø1,5 (Y 104,30; Z 23,92), dari boss gear cover X≈19,5 sampai lubang dudukan X≈30,5. As belakang = poros spur.
  - Bay baterai: lantai atas Z 6,76, dinding depan Y 36,97, belakang Y 90,92 (dinding depan dudukan). AA duduk di lantai:
    pusat Z 14,01, Y 63,945, X 31,75/46,25.
  - Tali penahan baterai di T0 ada di Z 18,795–19,295 (memotong baterai 2,5 mm), jadi dipasang di T0 + (0; 0; 2,5).
  - Lubang roller: depan (X 4,47/73,56; Y 3,12) & cadangan (X 2,0/76,02; Y 6,26) r 1; bumper belakang (X 15,89/62,15; Y 133,18) r 2,75.
- Model FA-130 (`models/web/fa130.glb`, skala 0,1346): **poros keluaran + boss di +z**, tutup belakang + tab terminal di −z;
  kaleng z −2,086…+1,303; lebar 20 mm di x, sisi datar 15 mm di y (tab sampai y 1,22).

## Selesai 24–25 Okt
1. Masalah lama no. 1: super1.glb dikonversi ulang, semua part pelengkap di posisi rakit (T0), titik asal & skala baru.
2. No. 2 & 6: gear di poros aslinya di dalam gear cover (pinion di poros dinamo, counter dua tingkat, spur di as; jari-jari
   saling bertaut, rasio diatur lewat pembagian counter kecil : spur). "Bundaran melayang" = cakram warna dinamo yang dulu
   ditaruh di ujung poros karena model FA-130 dibalik (poros mengarah menjauhi gear). Sekarang tidak dibalik; untuk sasis
   versi kode poros juga kini mengarah ke gear.
3. No. 3: baterai duduk di lantai bay (dasar y 0,617 > dasar sasis 0,262), di antara dinding bay, tali penahan di atasnya.
4. Roller Super-1 di lubang terukur (rumus lama berbasis bbox akan menaruh roller belakang 2 satuan di belakang lubangnya).
5. Titik pasang ada di `mount` pada entri sasis `super1` (`index.html`), dipakai lewat `MT` di `buildCar`.
6. **Aset 3D Baru Dikonversi & Dibuat (25 Okt)**:
   - `models/web/sliding-spoiler.glb` + `.js` (dari `Mini_4WD_sliding_spoiler.stl`, 24 KB Draco, titik asal terpusat).
   - `models/work/racing_raw.glb` (dari `Mini 4WD Racing.stp`, 33 part CAD terpisah dengan material asli).
   - `models/web/wheel-6spoke.glb` + `.js` (roda 6-spoke balap terpisah `rim` dan `tire`, skala simulator, 57 KB Draco).
   - `models/web/wheel-cyclone.glb` + `.js` (roda 5-spoke spiral Magnum terpisah `rim` dan `tire`, skala simulator, 50 KB Draco).
   - `models/web/wheel-3spoke.glb` + `.js` (roda 3-spoke presisi dari CAD SolidWorks `Velg.SLDPRT` & `Tire.SLDPRT`, 32 KB Draco, 3 hollow window cutout, outer rim 20 mm, tire 22 mm).
   - `models/web/roller-13mm.glb` + `.js` (guide roller 13 mm 3-spoke dari CAD SolidWorks `Piringan.SLDPRT`, 17 KB Draco, alur ekuator pemandu dinding, sumbu putar Y).
   - `models/web/roller-19mm.glb` + `.js` (guide roller 19 mm 6-hole aero lightweight aluminium, 20 KB Draco, alur O-ring luar, sumbu putar Y).
   - `models/web/fa130-pro.glb` + `.js` (dinamo Mabuchi FA-130 PRO double shaft simetris untuk sasis MS/MA mid-ship, 276 KB Draco).
   - `models/web/gear-pinion.glb` + `.js` (pinion gear 8T presisi dari CAD `racing_raw.glb`, 9 KB Draco).
   - `models/web/gear-counter.glb` + `.js` (counter gear dua tingkat dari CAD `racing_raw.glb`, 31 KB Draco).
   - `models/web/gear-spur.glb` + `.js` (spur gear as roda belakang dari CAD `racing_raw.glb`, 32 KB Draco).
   - `models/web/gear-set.glb` + `.js` (set lengkap 3 gear dalam konfigurasi meshed/terpasang, 72 KB Draco).
   - `models/web/mass-damper.glb` + `.js` (damper pemberat kuningan bertingkat + tiang stainless + locknut + bola stabilizer, 9 KB Draco).
   - `models/web/battery-aa.glb` + `.js` (baterai AA dari CAD `Battery.SLDPRT`, terpisah `body` dan `terminals`, 4 KB Draco).
   - `models/web/plate-frp-front.glb` + `.js` (bumper plate FRP depan multi-roller setting stay, 7 KB Draco).
   - `models/web/plate-frp-rear.glb` + `.js` (bumper plate FRP belakang multi-roller stay, 6 KB Draco).
   - `models/web/terminals.glb` + `.js` (plat kontak tembaga motor/baterai & tuas saklar dari CAD `racing_raw.glb`, 33 KB Draco).

## Catatan SolidWorks (.SLDPRT)
- Parser pure-Python `sw2fc` berhasil mengekstrak seluruh aliran Parasolid XT, PreviewPNG, dan pengukuran geometris presisi (silinder, torus, lingkaran, bidang) dari 24/26 file `.SLDPRT` di `models/source/tamiya15-solidworks/Part/`.
- Seluruh dimensi CAD asli (radius barel, diameter hub, fillet torus, sudut cutout) dapat direkonstruksi 100% presisi matematis ke Blender dan diekspor ke Draco GLB web tanpa perlu instalasi SolidWorks berbayar.

## Masalah terbuka
1. Body Magnum: atap sisi kiri belakang terlalu rendah. Gear cover dan dudukan dinamo menembus ±8–9 mm
   (pilihan: modifikasi mesh STL melengkungkan atap di atas gear, atau potong/hilangkan flap mesin).
2. Wire-up opsi part baru (`wheel-6spoke`, `wheel-cyclone`, `wheel-3spoke`, `roller-13mm`, `roller-19mm`, `fa130-pro`, `mass-damper`, `gear-set`) ke `index.html` dapat dilakukan kapan saja tanpa mengubah logika inti.

   (x −2,7…−4,8; z 1,7–2,0), sama besarnya dengan sebelum koreksi (uji peta tinggi body di browser). Body sayap aman
   (`python tools/body_clearance.py 0.9 1.05 1.28 1.12` → 0,00). → naikkan/potong body Magnum lokal.
2. Plate FRP: kalau tidak muat tanpa dipaksa, jangan dipakai. Plate belakang sekarang ada di lubang roller bumper; cek tabrakan dengan bumper.
3. Kecil: model FA-130 masih skala 0,1346 (1 % lebih kecil dari sasis); tabung kait penahan baterai bersinggungan
   0,5 mm dengan bibir dinding; struktur dalam gear cover (rusuk) tidak mencerminkan gear asli, jadi gear menembus rusuk
   dalam (tak terlihat saat cover terpasang).

## Cara kerja hemat token (penting, kuota user terbatas)
- Kerjakan SATU masalah per sesi; workflow/agen paralel hanya kalau diminta (sesi 24 Okt: 2 agen verifikasi, atas permintaan).
- Hindari screenshot berulang; cek dengan angka (`window.__g`, skrip Python) dulu.
- Mesh gear cover tidak rapat: voxel paritas sinar Z memberi isi palsu; pakai potongan bidang / jarak ke permukaan.
- User berbahasa Indonesia.
