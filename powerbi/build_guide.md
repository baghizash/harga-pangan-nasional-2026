# Panduan Membangun Dashboard — Power BI Desktop

## 1. Persiapan (5 menit)
1. Buka Power BI Desktop → Get Data → Text/CSV → impor kelima CSV di folder ini:
   `fact_nasional.csv`, `fact_provinsi.csv`, `dim_komoditas.csv`, `dim_provinsi.csv`, `dim_tanggal.csv`.
2. Pastikan tipe data: `harga_rp_per_kg` = Whole Number; `tanggal` = Date; lainnya Text.
3. Buka Model view. Buat relasi (semuanya satu-ke-banyak, single direction):
   - `dim_tanggal[tanggal]` → `fact_nasional[tanggal]`
   - `dim_komoditas[komoditas_id]` → `fact_nasional[komoditas_id]`
   - `dim_tanggal[tanggal]` → `fact_provinsi[tanggal]`
   - `dim_komoditas[komoditas_id]` → `fact_provinsi[komoditas_id]`
   - `dim_provinsi[provinsi_id]` → `fact_provinsi[provinsi_id]`
4. Klik kanan `dim_tanggal` → Mark as Date Table (kolom `tanggal`).

## 2. Measures (10 menit)
1. Salin seluruh blok DAX dari `measures_dax.md` ke dalam model (buat dua tabel measure atau gunakan folder display: "Nasional" dan "Provinsi").
2. Baca bagian "Catatan level" di `measures_dax.md` SEBELUM membuat visual — ini mencegah jebakan grain ganda.
3. Uji cepat: buat card dengan `Rata-rata Nasional 2026` + slicer Kelompok = Beras → harus **Rp15.983**. Jika beda, cek relasi.

## 3. Bangun 4 halaman (30–45 menit)
Ikuti `dashboard_layout.md` halaman per halaman:
- Halaman 1–2: HANYA field dari `fact_nasional` + measures NASIONAL.
- Halaman 3: HANYA field dari `fact_provinsi` + measures PROVINSI.
- Halaman 4: gabungan tampilan ringkas + tabel metodologi (ketik manual dari `dashboard_layout.md`).

## 4. Verifikasi akhir (10 menit)
- [ ] Halaman 1 KPI: Beras +3,0% / Daging Sapi +6,0% / Minyak Goreng +6,7% / Gula Pasir +2,4%.
- [ ] Halaman 2: Minyak Goreng Curah CV 4,3% (tertinggi); puncak 13–14 Okt 2026 tersorot.
- [ ] Halaman 3: gap Beras 40,2% (NTB vs Kalteng).
- [ ] Tidak ada visual yang mencampur `fact_nasional` dan `fact_provinsi` dalam satu agregasi.
- [ ] Simpan sebagai `Harga-Pangan-Nasional-2026.pbix` (file .pbix tidak di-push ke GitHub — GitHub tidak bisa me-render-nya; simpan screenshot dashboard sebagai gantinya bila perlu).

## Troubleshooting
- **Slicer Provinsi kosong di halaman nasional**: wajar — tidak ada relasi provinsi di `fact_nasional`. Hapus slicer itu dari halaman 1–2.
- **Angka tidak cocok dengan README**: pastikan visual memakai tabel fakta yang benar (nasional vs provinsi) dan filter Tahun = 2026 untuk KPI YoY.
- **Tanggal tidak urut di sumbu X**: pastikan `dim_tanggal` ditandai sebagai date table dan sumbu memakai `dim_tanggal[tanggal]`.
