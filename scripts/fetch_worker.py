#!/usr/bin/env python3
"""Parallel fetch worker: fetches a subset of commodities (by index into COMMODITIES).
Usage: fetch_worker.py <idx_start> <idx_end>   (end exclusive)
Shares the same chunk cache dir, so workers never duplicate work.
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/harga-pangan/scripts")
import time, json
from datetime import datetime
from fetch_pihps import (COMMODITIES, PROVINCES, CHUNKS, DELAY, fetch, parse_price)

def main():
    s, e = int(sys.argv[1]), int(sys.argv[2])
    subset = COMMODITIES[s:e]
    total = len(subset) * len(PROVINCES)
    n = 0
    for com_id, com_name in subset:
        for prov_id, prov_name in PROVINCES:
            n += 1
            cache = CHUNKS / f"{com_id}_{prov_id}.json"
            def has_province(d):
                return d is not None and any(r.get("level") == 1 for r in d.get("data", []))
            data = None
            if cache.exists():
                data = json.loads(cache.read_text())
                if not has_province(data):
                    cache.unlink(); data = None
                else:
                    print(f"[w{s}-{e} {n}/{total}] {com_name}/{prov_name}: cached", flush=True)
                    continue
            for attempt in range(2):
                data = fetch(com_id, prov_id)
                if has_province(data):
                    break
                print(f"  attempt {attempt+1}/2: no province row, retrying", flush=True)
                time.sleep(5)
            if not has_province(data):
                print(f"[w{s}-{e} {n}/{total}] {com_name}/{prov_name}: GAP", flush=True)
                (CHUNKS / f"GAP_{com_id}_{prov_id}.txt").write_text("no level-1 row")
                continue
            cache.write_text(json.dumps(data, ensure_ascii=False))
            print(f"[w{s}-{e} {n}/{total}] {com_name}/{prov_name}: fetched", flush=True)
            time.sleep(DELAY)

if __name__ == "__main__":
    main()
