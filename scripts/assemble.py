#!/usr/bin/env python3
"""Assemble tidy CSVs from cached PIHPS chunk JSONs (no network)."""
import json, csv
from datetime import datetime
from pathlib import Path

ROOT = Path("/home/hatch/workspace/harga-pangan")
CHUNKS = ROOT / "data" / "raw" / "pihps_chunks"

COMMODITIES = [
    ("com_1", "Beras Kualitas Bawah I"), ("com_2", "Beras Kualitas Bawah II"),
    ("com_3", "Beras Kualitas Medium I"), ("com_4", "Beras Kualitas Medium II"),
    ("com_5", "Beras Kualitas Super I"), ("com_6", "Beras Kualitas Super II"),
    ("com_8", "Daging Sapi Kualitas 1"), ("com_9", "Daging Sapi Kualitas 2"),
    ("com_17", "Minyak Goreng Curah"), ("com_18", "Minyak Goreng Kemasan Bermerk 1"),
    ("com_19", "Minyak Goreng Kemasan Bermerk 2"),
    ("com_20", "Gula Pasir Kualitas Premium"), ("com_21", "Gula Pasir Lokal"),
]
PROVINCES = [
    (1, "Aceh"), (2, "Sumatera Utara"), (3, "Sumatera Barat"), (4, "Riau"),
    (5, "Kepulauan Riau"), (6, "Jambi"), (7, "Bengkulu"), (8, "Sumatera Selatan"),
    (9, "Kepulauan Bangka Belitung"), (10, "Lampung"), (11, "Banten"),
    (12, "Jawa Barat"), (13, "DKI Jakarta"), (14, "Jawa Tengah"),
    (15, "DI Yogyakarta"), (16, "Jawa Timur"), (17, "Bali"),
    (18, "Nusa Tenggara Barat"), (19, "Nusa Tenggara Timur"),
    (20, "Kalimantan Barat"), (21, "Kalimantan Selatan"), (22, "Kalimantan Tengah"),
    (23, "Kalimantan Timur"), (24, "Kalimantan Utara"), (25, "Gorontalo"),
    (26, "Sulawesi Selatan"), (27, "Sulawesi Tenggara"), (28, "Sulawesi Tengah"),
    (29, "Sulawesi Utara"), (30, "Sulawesi Barat"), (31, "Maluku"),
    (32, "Maluku Utara"), (33, "Papua"), (34, "Papua Barat"),
]

def parse_price(v):
    if v is None or str(v).strip() in ("", "-", "0"):
        return None
    return int(str(v).replace(",", "").replace(".", ""))

rows, national_rows, gaps = [], [], []
for com_id, com_name in COMMODITIES:
    for prov_id, prov_name in PROVINCES:
        cache = CHUNKS / f"{com_id}_{prov_id}.json"
        if not cache.exists():
            gaps.append((com_id, prov_id))
            continue
        data = json.loads(cache.read_text())
        for row in data.get("data", []):
            lvl = row.get("level")
            for k, v in row.items():
                if k in ("no", "name", "level"):
                    continue
                try:
                    dt = datetime.strptime(k, "%d/%m/%Y").date().isoformat()
                except ValueError:
                    continue
                price = parse_price(v)
                rec = {"tanggal": dt, "komoditas_id": com_id, "komoditas": com_name,
                       "provinsi_id": prov_id, "provinsi": prov_name,
                       "level": lvl, "harga_rp_per_kg": price}
                if lvl == 0:
                    national_rows.append(rec)
                elif lvl == 1:
                    rows.append(rec)

seen, nat = set(), []
for rec in national_rows:
    key = (rec["tanggal"], rec["komoditas_id"])
    if key not in seen:
        seen.add(key)
        nat.append({**rec, "provinsi_id": 0, "provinsi": "Nasional"})

FIELDS = ["tanggal", "komoditas_id", "komoditas", "provinsi_id", "provinsi", "level", "harga_rp_per_kg"]
with open(ROOT / "data" / "raw" / "harga_pangan_provinsi.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
with open(ROOT / "data" / "raw" / "harga_pangan_nasional.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(nat)
print(f"provincial rows: {len(rows)}")
print(f"national rows: {len(nat)}")
print(f"gaps (no chunk): {gaps}")
# sanity: date range per commodity (national)
from collections import defaultdict
rng = defaultdict(list)
for r in nat:
    rng[r["komoditas_id"]].append(r["tanggal"])
for cid, _ in COMMODITIES:
    ds = sorted(rng[cid])
    print(cid, len(ds), ds[0] if ds else "-", ds[-1] if ds else "-")
