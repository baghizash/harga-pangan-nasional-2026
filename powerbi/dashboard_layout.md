# Dashboard Layout — Harga Pangan Nasional 2026 (4 halaman, 16:9)

Palet: teal gelap `#0E7C7B` (primer), amber `#D9A441` (aksen), slate `#3A6EA5`, bata `#C1553B`.
Font: Segoe UI / Calibri. Satu ide per halaman, judul rata kiri, angka kunci besar.

## Halaman 1 — Ringkasan Nasional
- **KPI cards (4)**: Rata-rata Nasional 2026 + YoY % per kelompok (Beras, Daging Sapi, Minyak Goreng, Gula Pasir). Angka acuan: Beras Rp15.983 (+3,0%), Daging Sapi Rp144.214 (+6,0%), Minyak Goreng Rp22.146 (+6,7%), Gula Pasir Rp19.539 (+2,4%).
- **Line chart**: tren harian indeks per kelompok (measure: Rata-rata Nasional; sumbu X dim_tanggal[tanggal]; legend dim_komoditas[kelompok]).
- **Slicers**: Tahun, Kelompok. (Sumber: `fact_nasional`.)
- Catatan kaki: "Sumber: PIHPS/BI, pasar tradisional, 1 Jan 2025 – 19 Okt 2026."

## Halaman 2 — Volatilitas & Puncak
- **Bar chart horizontal**: Volatilitas CV % Nasional per komoditas (tertinggi: Minyak Goreng Curah 4,3%; terendah: Gula Pasir Premium 1,3%).
- **Tabel**: Komoditas | Harga Maks Nasional | Tanggal Maks Nasional. Sorot baris puncak 13–14 Okt 2026 (lonjakan serentak keempat kelompok).
- **Line chart kecil**: Minyak Goreng Curah vs Kemasan (kontras volatilitas curah).
- (Sumber: `fact_nasional`.)

## Halaman 3 — Disparitas Provinsi
- **Peta (filled map)**: Rata-rata Provinsi per provinsi, warna gradasi teal. Slicer Kelompok wajib.
- **Bar chart**: 5 provinsi termahal vs 5 termurah (measure Peringkat Provinsi). Acuan: Beras NTB Rp13.622 vs Kalteng Rp19.094 (gap 40,2%); Daging Sapi NTT vs Kalsel (gap 40,8%).
- **KPI**: Selisih Termahal vs Termurah %.
- **Slicers**: Kelompok, Provinsi (multi-select). (Sumber: `fact_provinsi`. Jangan campur dengan halaman 1.)

## Halaman 4 — Musiman & Metodologi
- **Clustered bar**: harga 30 hari sebelum / selama / sesudah Ramadan 2025 & 2026 per kelompok (efek kecil: beras +0,2–0,4%).
- **Tabel metodologi**: sumber data, periode, cakupan (pasar tradisional), keterbatasan (9 pasangan komoditas-provinsi tanpa seri; "-" = tidak lapor).
- **Tombol navigasi** kembali ke Halaman 1.

## Aturan konsisten
- Judul halaman: 20pt bold, rata kiri, warna slate gelap.
- Angka KPI: 28pt bold teal; satuan Rp/kg; persen 1 desimal.
- Tidak ada slicer Provinsi di Halaman 1–2; tidak ada visual nasional di Halaman 3.
