#!/usr/bin/env python3
"""Fetch daily staple-food prices from the official PIHPS / Bank Indonesia public API.

Endpoint discovered from the public PIHPS website (hargapangan.id):
  GET https://www.bi.go.id/hargapangan/WebSite/TabelHarga/GetGridDataKomoditas
  ?price_type_id=1 (Pasar Tradisional)
  &comcat_id=<one leaf id>  (leaf commodities, NOT category averages)
  &province_id=<id>  (one province per call; comma lists are ignored by the API)
  &showKota=false &showPasar=false &tipe_laporan=1 (daily)
  &start_date=YYYY-MM-DD &end_date=YYYY-MM-DD

Each call returns {"data": [national row (level 0), province row (level 1)]}
with one column per reporting date (DD/MM/YYYY). "-" means no report that day.
No authentication is required. This script only READS the public API; it does
not copy any third-party dataset.

Leaf commodities verified 2026-10-19 from the PIHPS site catalog
(www.bi.go.id/hargapangan embedded PIHPS_Category JSON). There are NO leaf
commodities for telur ayam, daging ayam, or bawang merah/bawang putih in this
API -- only category aggregates. Those are deliberately NOT used.

Output:
  data/raw/pihps_chunks/{commodity}_{province_id}.json  (raw API responses)
  data/raw/harga_pangan_provinsi.csv  (tidy long-format table, level 1)
  data/raw/harga_pangan_nasional.csv  (national series, level 0)
"""
import json, time, urllib.request, urllib.parse, http.cookiejar, sys
from datetime import datetime
from pathlib import Path

BASE = "https://www.bi.go.id/hargapangan"
ROOT = Path(__file__).resolve().parent.parent
CHUNKS = ROOT / "data" / "raw" / "pihps_chunks"
CHUNKS.mkdir(parents=True, exist_ok=True)

COMMODITIES = [
    ("com_1", "Beras Kualitas Bawah I"),
    ("com_2", "Beras Kualitas Bawah II"),
    ("com_3", "Beras Kualitas Medium I"),
    ("com_4", "Beras Kualitas Medium II"),
    ("com_5", "Beras Kualitas Super I"),
    ("com_6", "Beras Kualitas Super II"),
    ("com_8", "Daging Sapi Kualitas 1"),
    ("com_9", "Daging Sapi Kualitas 2"),
    ("com_17", "Minyak Goreng Curah"),
    ("com_18", "Minyak Goreng Kemasan Bermerk 1"),
    ("com_19", "Minyak Goreng Kemasan Bermerk 2"),
    ("com_20", "Gula Pasir Kualitas Premium"),
    ("com_21", "Gula Pasir Lokal"),
]
# Commodity groups for analysis
GROUPS = {
    "Beras": ["com_1", "com_2", "com_3", "com_4", "com_5", "com_6"],
    "Daging Sapi": ["com_8", "com_9"],
    "Minyak Goreng": ["com_17", "com_18", "com_19"],
    "Gula Pasir": ["com_20", "com_21"],
}
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
START, END = "2025-01-01", "2026-10-19"
DELAY = 1.2

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
HDRS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE}/TabelHarga/PasarTradisionalKomoditas",
}


def fetch(comcat, prov_id, tries=3):
    params = {"price_type_id": 1, "comcat_id": comcat, "province_id": prov_id,
              "regency_id": "", "showKota": "false", "showPasar": "false",
              "tipe_laporan": 1, "start_date": START, "end_date": END,
              "_": int(time.time() * 1000)}
    url = f"{BASE}/WebSite/TabelHarga/GetGridDataKomoditas?" + urllib.parse.urlencode(params)
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            with opener.open(req, timeout=300) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            print(f"  retry {attempt+1}/{tries}: {e}", flush=True)
            time.sleep(5)
    return None


def parse_price(v):
    if v is None or str(v).strip() in ("", "-", "0"):
        return None
    return int(str(v).replace(",", "").replace(".", ""))


def main():
    req = urllib.request.Request(f"{BASE}/TabelHarga/PasarTradisionalKomoditas", headers=HDRS)
    with opener.open(req, timeout=90) as r:
        r.read()
    print("session established", flush=True)

    rows, national_rows = [], []
    total = len(COMMODITIES) * len(PROVINCES)
    n = 0
    for com_id, com_name in COMMODITIES:
        for prov_id, prov_name in PROVINCES:
            n += 1
            cache = CHUNKS / f"{com_id}_{prov_id}.json"
            def has_province(d):
                return d is not None and any(r.get("level") == 1 for r in d.get("data", []))
            if cache.exists():
                data = json.loads(cache.read_text())
                if not has_province(data):
                    print(f"[{n}/{total}] {com_name} / {prov_name}: cached response lacks province row, refetching", flush=True)
                    cache.unlink()
                    data = None
                else:
                    print(f"[{n}/{total}] {com_name} / {prov_name}: cached", flush=True)
            else:
                data = None
            if data is None:
                for attempt in range(2):
                    data = fetch(com_id, prov_id)
                    if has_province(data):
                        break
                    print(f"  attempt {attempt+1}/2: no province row, retrying", flush=True)
                    time.sleep(5)
                if not has_province(data):
                    print(f"[{n}/{total}] {com_name} / {prov_name}: NO PROVINCE SERIES after retries (recorded as gap)", flush=True)
                    (CHUNKS / f"GAP_{com_id}_{prov_id}.txt").write_text("no level-1 row after 2 attempts")
                    continue
                cache.write_text(json.dumps(data, ensure_ascii=False))
                print(f"[{n}/{total}] {com_name} / {prov_name}: fetched {len(data.get('data', []))} rows", flush=True)
                time.sleep(DELAY)
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
    # National series: identical in every province call; keep first occurrence per (date, commodity)
    seen, nat = set(), []
    for rec in national_rows:
        key = (rec["tanggal"], rec["komoditas_id"])
        if key not in seen:
            seen.add(key)
            nat.append({**rec, "provinsi_id": 0, "provinsi": "Nasional"})
    import csv
    out = ROOT / "data" / "raw" / "harga_pangan_provinsi.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["tanggal", "komoditas_id", "komoditas", "provinsi_id", "provinsi", "level", "harga_rp_per_kg"])
        w.writeheader()
        w.writerows(rows)
    out2 = ROOT / "data" / "raw" / "harga_pangan_nasional.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["tanggal", "komoditas_id", "komoditas", "provinsi_id", "provinsi", "level", "harga_rp_per_kg"])
        w.writeheader()
        w.writerows(nat)
    print(f"provincial rows: {len(rows)} -> {out}", flush=True)
    print(f"national rows: {len(nat)} -> {out2}", flush=True)


if __name__ == "__main__":
    main()
