#!/usr/bin/env python3
"""Load the PIHPS CSVs into SQLite with a clean star schema.

Tables:
  dim_komoditas(komoditas_id PK, komoditas, kelompok)
  dim_provinsi(provinsi_id PK, provinsi)
  dim_tanggal(tanggal PK, tahun, bulan, hari)
  fact_nasional(tanggal, komoditas_id, harga_rp_per_kg)      -- level nasional SAJA
  fact_provinsi(tanggal, komoditas_id, provinsi_id, harga_rp_per_kg)  -- level provinsi SAJA

Design rule (lesson from the cabai project): national and province grains live
in SEPARATE fact tables from the start. No aggregate rows inside detail tables,
so every SUM/AVG/MAX measure reads exactly one grain with no guard needed.
"""
import csv, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "harga_pangan.db"

GROUPS = {
    "Beras": ["com_1", "com_2", "com_3", "com_4", "com_5", "com_6"],
    "Daging Sapi": ["com_8", "com_9"],
    "Minyak Goreng": ["com_17", "com_18", "com_19"],
    "Gula Pasir": ["com_20", "com_21"],
}
COM2GRP = {c: g for g, cs in GROUPS.items() for c in cs}


def main():
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE dim_komoditas(komoditas_id TEXT PRIMARY KEY, komoditas TEXT, kelompok TEXT);
        CREATE TABLE dim_provinsi(provinsi_id INTEGER PRIMARY KEY, provinsi TEXT);
        CREATE TABLE dim_tanggal(tanggal TEXT PRIMARY KEY, tahun INTEGER, bulan INTEGER, hari INTEGER);
        CREATE TABLE fact_nasional(tanggal TEXT, komoditas_id TEXT, harga_rp_per_kg INTEGER,
            PRIMARY KEY (tanggal, komoditas_id));
        CREATE TABLE fact_provinsi(tanggal TEXT, komoditas_id TEXT, provinsi_id INTEGER, harga_rp_per_kg INTEGER,
            PRIMARY KEY (tanggal, komoditas_id, provinsi_id));
    """)
    with open(ROOT / "data" / "raw" / "harga_pangan_nasional.csv", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        coms, dates, nat = {}, set(), []
        for r in rdr:
            if not r["harga_rp_per_kg"]:
                continue
            coms[r["komoditas_id"]] = r["komoditas"]
            dates.add(r["tanggal"])
            nat.append((r["tanggal"], r["komoditas_id"], int(r["harga_rp_per_kg"])))
    with open(ROOT / "data" / "raw" / "harga_pangan_provinsi.csv", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        provs, prow = {}, []
        for r in rdr:
            if not r["harga_rp_per_kg"]:
                continue
            coms[r["komoditas_id"]] = r["komoditas"]
            provs[int(r["provinsi_id"])] = r["provinsi"]
            dates.add(r["tanggal"])
            prow.append((r["tanggal"], r["komoditas_id"], int(r["provinsi_id"]), int(r["harga_rp_per_kg"])))
    cur.executemany("INSERT INTO dim_komoditas VALUES (?,?,?)",
                    [(cid, nm, COM2GRP.get(cid, "?")) for cid, nm in coms.items()])
    cur.executemany("INSERT INTO dim_provinsi VALUES (?,?)", list(provs.items()))
    cur.executemany("INSERT INTO dim_tanggal VALUES (?,?,?,?)",
                    [(d, int(d[:4]), int(d[5:7]), int(d[8:10])) for d in sorted(dates)])
    cur.executemany("INSERT INTO fact_nasional VALUES (?,?,?)", nat)
    cur.executemany("INSERT INTO fact_provinsi VALUES (?,?,?,?)", prow)
    con.commit()
    for t in ["dim_komoditas", "dim_provinsi", "dim_tanggal", "fact_nasional", "fact_provinsi"]:
        print(t, cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
    con.close()
    print("db:", DB)


if __name__ == "__main__":
    main()
