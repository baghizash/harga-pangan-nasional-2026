# DAX Measures — Harga Pangan Nasional 2026

## Catatan level (PENTING — baca dulu)

Model ini memakai **dua tabel fakta terpisah sejak desain** (pelajaran dari proyek Harga Cabai):

| Tabel fakta | Grain (1 baris =) | Untuk visual... |
|---|---|---|
| `fact_nasional` | 1 tanggal × 1 komoditas (seri nasional) | Tren nasional, YoY, puncak, volatilitas NASIONAL |
| `fact_provinsi` | 1 tanggal × 1 komoditas × 1 provinsi | Perbandingan antarprovinsi, peta, disparitas |

**Tidak ada baris "Nasional" di dalam `fact_provinsi` dan tidak ada baris provinsi di dalam `fact_nasional`.** Karena itu setiap measure di bawah membaca tepat satu grain — tidak perlu guard/filter level seperti pada proyek cabai. Jangan menggabungkan kedua tabel fakta dalam satu visual tanpa memikirkan grain-nya.

Relasi: `dim_tanggal[tanggal]` 1—* `fact_nasional[tanggal]`, `dim_komoditas[komoditas_id]` 1—* `fact_nasional[komoditas_id]`; sama untuk `fact_provinsi` + `dim_provinsi[provinsi_id]` 1—* `fact_provinsi[provinsi_id]`. `dim_tanggal` ditandai sebagai tabel tanggal.

## Verifikasi angka (dihitung dari CSV kit ini)

| Kelompok | Rata-rata 2025 | Rata-rata 2026 | YoY | Puncak (nasional) |
|---|---|---|---|---|
| Beras | Rp15.515 | Rp15.990 | +3,1% | Rp16.367 (13 Okt 2026) |
| Daging Sapi | Rp136.093 | Rp144.290 | +6,0% | Rp148.600 (13 Okt 2026) |
| Minyak Goreng | Rp20.753 | Rp22.158 | +6,8% | Rp22.850 (13 Okt 2026) |
| Gula Pasir | Rp19.086 | Rp19.547 | +2,4% | Rp20.000 (21 Okt 2026) |

Visual nasional 2026 WAJIB menampilkan angka di atas. Jika berbeda, cek: visual memakai `fact_nasional` (bukan `fact_provinsi`).

## Measures — NASIONAL (tabel `fact_nasional`)

```dax
Rata-rata Nasional =
AVERAGE ( fact_nasional[harga_rp_per_kg] )

Rata-rata Nasional 2025 =
CALCULATE ( [Rata-rata Nasional], dim_tanggal[tahun] = 2025 )

Rata-rata Nasional 2026 =
CALCULATE ( [Rata-rata Nasional], dim_tanggal[tahun] = 2026 )

YoY % =
DIVIDE (
    [Rata-rata Nasional 2026] - [Rata-rata Nasional 2025],
    [Rata-rata Nasional 2025]
)

Harga Maks Nasional =
MAX ( fact_nasional[harga_rp_per_kg] )

Tanggal Maks Nasional =
MAXX (
    TOPN ( 1, fact_nasional, fact_nasional[harga_rp_per_kg], DESC ),
    fact_nasional[tanggal]
)

Volatilitas CV % Nasional =
DIVIDE (
    STDEV.P ( fact_nasional[harga_rp_per_kg] ),
    AVERAGE ( fact_nasional[harga_rp_per_kg] )
) * 100
```

## Measures — PROVINSI (tabel `fact_provinsi`)

```dax
Rata-rata Provinsi =
AVERAGE ( fact_provinsi[harga_rp_per_kg] )

Provinsi Termahal =
MAXX (
    TOPN ( 1, SUMMARIZE ( fact_provinsi, dim_provinsi[provinsi], "r", [Rata-rata Provinsi] ), [r], DESC ),
    dim_provinsi[provinsi]
)

Selisih Termahal vs Termurah % =
VAR t =
    SUMMARIZE ( fact_provinsi, dim_provinsi[provinsi], "r", [Rata-rata Provinsi] )
RETURN
    DIVIDE ( MAXX ( t, [r] ) - MINX ( t, [r] ), MINX ( t, [r] ) ) * 100

Peringkat Provinsi =
RANKX (
    ALL ( dim_provinsi[provinsi] ),
    [Rata-rata Provinsi],
    ,
    DESC,
    DENSE
)
```

## Aturan pakai

1. Satu visual = satu tabel fakta. Visual nasional pakai measures NASIONAL; visual provinsi pakai measures PROVINSI.
2. Slicer Tahun/Komoditas/Kelompok boleh dipakai di kedua jenis visual (relasi via dimensi).
3. Slicer Provinsi HANYA untuk visual provinsi — jangan pasang di halaman nasional (tidak ada relasi provinsi di `fact_nasional`, slicer akan kosong).
4. Uji tiap measure pada satu komoditas + satu tahun dulu sebelum membangun halaman penuh (contoh: Beras, 2026 → rata-rata nasional harus Rp15.990).
