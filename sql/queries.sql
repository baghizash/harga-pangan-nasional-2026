-- ============================================================
-- Harga Pangan Nasional 2026 — SQL analitik
-- Database: SQLite (dibangun dari data/raw/*.csv via scripts/load_to_sqlite.py)
-- Tabel: fact_nasional(tanggal, komoditas_id, komoditas, harga_rp_per_kg),
--        fact_provinsi(tanggal, komoditas_id, komoditas, provinsi_id, provinsi, harga_rp_per_kg),
--        dim_komoditas(komoditas_id, komoditas, kelompok),
--        dim_provinsi(provinsi_id, provinsi)
-- Level nasional dan provinsi DIPISAH sejak desain (pelajaran dari proyek cabai):
-- tidak ada baris agregat di dalam tabel detail, jadi agregasi aman.
-- ============================================================

-- 1. Rata-rata nasional 2025 vs 2026 + YoY per kelompok komoditas
SELECT k.kelompok,
       ROUND(AVG(CASE WHEN strftime('%Y', n.tanggal) = '2025' THEN n.harga_rp_per_kg END)) AS rata_2025,
       ROUND(AVG(CASE WHEN strftime('%Y', n.tanggal) = '2026' THEN n.harga_rp_per_kg END)) AS rata_2026,
       ROUND((AVG(CASE WHEN strftime('%Y', n.tanggal) = '2026' THEN n.harga_rp_per_kg END)
            - AVG(CASE WHEN strftime('%Y', n.tanggal) = '2025' THEN n.harga_rp_per_kg END))
            / AVG(CASE WHEN strftime('%Y', n.tanggal) = '2025' THEN n.harga_rp_per_kg END) * 100, 1) AS yoy_pct
FROM fact_nasional n
JOIN dim_komoditas k ON k.komoditas_id = n.komoditas_id
GROUP BY k.kelompok
ORDER BY yoy_pct DESC;

-- 2. Puncak harga nasional per komoditas (nilai + tanggal)
SELECT n.komoditas, MAX(n.harga_rp_per_kg) AS harga_maks,
       (SELECT tanggal FROM fact_nasional
         WHERE komoditas_id = n.komoditas_id
         ORDER BY harga_rp_per_kg DESC LIMIT 1) AS tanggal_maks
FROM fact_nasional n
GROUP BY n.komoditas_id, n.komoditas
ORDER BY harga_maks DESC;

-- 3. Volatilitas (koefisien variasi) per komoditas, seri nasional
SELECT komoditas,
       ROUND(AVG(harga_rp_per_kg)) AS rata2,
       ROUND((sqrt(AVG(harga_rp_per_kg*harga_rp_per_kg) - AVG(harga_rp_per_kg)*AVG(harga_rp_per_kg))
              / AVG(harga_rp_per_kg)) * 100, 1) AS cv_pct
FROM fact_nasional
GROUP BY komoditas_id, komoditas
ORDER BY cv_pct DESC;

-- 4. Disparitas provinsi 2026: 5 termurah vs 5 termahal per kelompok
WITH prov_avg AS (
  SELECT k.kelompok, p.provinsi, AVG(p.harga_rp_per_kg) AS rata
  FROM fact_provinsi p
  JOIN dim_komoditas k ON k.komoditas_id = p.komoditas_id
  WHERE strftime('%Y', p.tanggal) = '2026'
  GROUP BY k.kelompok, p.provinsi
),
ranked AS (
  SELECT kelompok, provinsi, ROUND(rata) AS rata,
         ROW_NUMBER() OVER (PARTITION BY kelompok ORDER BY rata) AS rn_asc,
         ROW_NUMBER() OVER (PARTITION BY kelompok ORDER BY rata DESC) AS rn_desc
  FROM prov_avg
)
SELECT kelompok, provinsi, rata,
       CASE WHEN rn_asc <= 5 THEN 'termurah' ELSE 'termahal' END AS sisi
FROM ranked WHERE rn_asc <= 5 OR rn_desc <= 5
ORDER BY kelompok, rata;

-- 5. Selisih % provinsi termahal vs termurah per kelompok (2026)
WITH prov_avg AS (
  SELECT k.kelompok, AVG(p.harga_rp_per_kg) AS rata
  FROM fact_provinsi p
  JOIN dim_komoditas k ON k.komoditas_id = p.komoditas_id
  WHERE strftime('%Y', p.tanggal) = '2026'
  GROUP BY k.kelompok, p.provinsi
)
SELECT kelompok,
       ROUND(MIN(rata)) AS termurah,
       ROUND(MAX(rata)) AS termahal,
       ROUND((MAX(rata) - MIN(rata)) / MIN(rata) * 100, 1) AS selisih_pct
FROM prov_avg
GROUP BY kelompok;

-- 6. Efek Ramadan: rata-rata 30 hari sebelum / selama / 30 hari sesudah
-- Ramadan 2025: 2025-03-01 s/d 2025-03-29 ; Ramadan 2026: 2026-02-18 s/d 2026-03-19
SELECT k.kelompok,
       '2025' AS tahun,
       ROUND(AVG(CASE WHEN n.tanggal BETWEEN '2025-01-30' AND '2025-02-28' THEN n.harga_rp_per_kg END)) AS sebelum,
       ROUND(AVG(CASE WHEN n.tanggal BETWEEN '2025-03-01' AND '2025-03-29' THEN n.harga_rp_per_kg END)) AS selama,
       ROUND(AVG(CASE WHEN n.tanggal BETWEEN '2025-03-30' AND '2025-04-28' THEN n.harga_rp_per_kg END)) AS sesudah
FROM fact_nasional n
JOIN dim_komoditas k ON k.komoditas_id = n.komoditas_id
GROUP BY k.kelompok
UNION ALL
SELECT k.kelompok,
       '2026' AS tahun,
       ROUND(AVG(CASE WHEN n.tanggal BETWEEN '2026-01-19' AND '2026-02-17' THEN n.harga_rp_per_kg END)),
       ROUND(AVG(CASE WHEN n.tanggal BETWEEN '2026-02-18' AND '2026-03-19' THEN n.harga_rp_per_kg END)),
       ROUND(AVG(CASE WHEN n.tanggal BETWEEN '2026-03-20' AND '2026-04-18' THEN n.harga_rp_per_kg END))
FROM fact_nasional n
JOIN dim_komoditas k ON k.komoditas_id = n.komoditas_id
GROUP BY k.kelompok;

-- 7. Tren bulanan nasional per kelompok (untuk chart tren)
SELECT k.kelompok, substr(n.tanggal, 1, 7) AS bulan,
       ROUND(AVG(n.harga_rp_per_kg)) AS rata_bulanan
FROM fact_nasional n
JOIN dim_komoditas k ON k.komoditas_id = n.komoditas_id
GROUP BY k.kelompok, bulan
ORDER BY k.kelompok, bulan;

-- 8. Kelengkapan data: jumlah hari terlaporkan per komoditas (nasional)
SELECT komoditas_id, komoditas, COUNT(*) AS n_hari,
       MIN(tanggal) AS awal, MAX(tanggal) AS akhir
FROM fact_nasional
GROUP BY komoditas_id, komoditas
ORDER BY komoditas_id;
