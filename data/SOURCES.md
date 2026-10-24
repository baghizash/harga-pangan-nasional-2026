# Sumber Data

Seluruh data dalam repo ini berasal dari **satu sumber resmi**: API publik
**PIHPS (Pusat Informasi Harga Pangan Strategis) / Bank Indonesia**.

- **Portal**: https://www.bi.go.id/hargapangan (juga dikenal sebagai hargapangan.id)
- **Endpoint**: `GET /hargapangan/WebSite/TabelHarga/GetGridDataKomoditas`
- **Parameter**: `price_type_id=1` (Pasar Tradisional), `tipe_laporan=1` (harian),
  `showKota=false`, `showPasar=false`, satu `comcat_id` + satu `province_id` per panggilan
- **Diakses**: 19–20 Oktober 2026, diperbarui 24 Oktober 2026 (read-only, tanpa autentikasi)
- **Periode**: 2025-01-01 s/d 2026-10-23 (API menyimpan data sejak 01/01/2018; periode
  proyek dibatasi 2025-01-01 sesuai kesepakatan agar sebanding dengan proyek Harga Cabai)
  Pembaruan 24 Okt 2026 menambah 4 hari laporan (20–23 Okt 2026); 24 Okt 2026
  jatuh pada hari Sabtu sehingga belum ada laporan PIHPS untuk tanggal itu.
- **Respons**: `{"data": [baris nasional (level 0), baris provinsi (level 1)]}`,
  satu kolom per tanggal laporan (DD/MM/YYYY); `"-"` = tidak ada laporan hari itu

## Berkas

| Berkas | Isi | Sumber |
|---|---|---|
| `data/raw/harga_pangan_nasional.csv` | Seri harian level nasional, 13 komoditas | Dididuplikasi dari baris level 0 tiap respons API |
| `data/raw/harga_pangan_provinsi.csv` | Seri harian 34 provinsi, 13 komoditas | Baris level 1 tiap respons API |
| `data/raw/pihps_chunks/*.json` | 442 respons mentah API (per komoditas × provinsi) | Langsung dari endpoint di atas |
| `data/raw/pihps_chunks/GAP_*.txt` | Pasangan komoditas-provinsi tanpa seri | Tercatat saat fetch (tidak ada baris level 1 setelah retry) |

## Komoditas (13, terverifikasi dari katalog situs PIHPS 2026-10-19)

Beras Kualitas Bawah I/II, Beras Kualitas Medium I/II, Beras Kualitas Super I/II
(com_1–com_6); Daging Sapi Kualitas 1/2 (com_8, com_9);
Minyak Goreng Curah, Kemasan Bermerk 1/2 (com_17–com_19);
Gula Pasir Kualitas Premium/Lokal (com_20, com_21).

Tidak ada komoditas daun untuk telur ayam, daging ayam, bawang merah, atau bawang
putih di API ini (hanya agregat kategori) — sengaja tidak dipakai dan tidak dikarang.

## Reproduksi

Jalankan `python3 scripts/fetch_pihps.py` (atau 8 worker `scripts/fetch_worker.py`)
untuk mengunduh ulang seluruh data mentah, lalu `python3 scripts/analyze.py`
untuk menghitung ulang `findings.json` dan seluruh chart dari nol.
