#!/usr/bin/env python3
"""Analyze Harga Pangan Nasional 2026: national trends, YoY, volatility,
province disparities, Ramadan/Lebaran effects, cross-commodity comparison.
Outputs: findings.json + charts/*.png. All numbers re-derived from fetched data.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = "/home/hatch/workspace/harga-pangan"
CHARTS = f"{ROOT}/charts"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linestyle": "--",
    "figure.dpi": 150,
})
# Palette: deep teal + warm amber + slate (no purple, no neon)
PAL = ["#0E7C7B", "#D9A441", "#3A6EA5", "#C1553B", "#5B8C5A", "#8A6FB8"]
PAL_TEAL = "#0E7C7B"

GROUPS = {
    "Beras": ["com_1", "com_2", "com_3", "com_4", "com_5", "com_6"],
    "Daging Sapi": ["com_8", "com_9"],
    "Minyak Goreng": ["com_17", "com_18", "com_19"],
    "Gula Pasir": ["com_20", "com_21"],
}
COM_NAMES = {
    "com_1": "Beras Kualitas Bawah I", "com_2": "Beras Kualitas Bawah II",
    "com_3": "Beras Kualitas Medium I", "com_4": "Beras Kualitas Medium II",
    "com_5": "Beras Kualitas Super I", "com_6": "Beras Kualitas Super II",
    "com_8": "Daging Sapi Kualitas 1", "com_9": "Daging Sapi Kualitas 2",
    "com_17": "Minyak Goreng Curah", "com_18": "Minyak Goreng Kemasan Bermerk 1",
    "com_19": "Minyak Goreng Kemasan Bermerk 2",
    "com_20": "Gula Pasir Kualitas Premium", "com_21": "Gula Pasir Lokal",
}
RAMADAN = [("2025-03-01", "2025-03-29"), ("2026-02-18", "2026-03-19")]
LEBARAN = ["2025-03-31", "2026-03-20"]


def rp(x):
    return f"Rp{x:,.0f}".replace(",", ".")


def main():
    nat = pd.read_csv(f"{ROOT}/data/raw/harga_pangan_nasional.csv", parse_dates=["tanggal"])
    prov = pd.read_csv(f"{ROOT}/data/raw/harga_pangan_provinsi.csv", parse_dates=["tanggal"])
    nat = nat.dropna(subset=["harga_rp_per_kg"])
    prov = prov.dropna(subset=["harga_rp_per_kg"])
    nat["tahun"] = nat["tanggal"].dt.year
    prov["tahun"] = prov["tanggal"].dt.year

    findings = {"periode": {"mulai": "2025-01-01", "selesai": "2026-10-19",
                            "sumber": "PIHPS / Bank Indonesia (API publik, pasar tradisional, harian)",
                            "komoditas": 13, "provinsi": 34},
                "kelompok": {}, "komoditas": {}, "provinsi": {},
                "ramadan": {}, "lintas_komoditas": {}}

    # ---------- per-commodity national stats ----------
    com_stats = {}
    for cid, cname in COM_NAMES.items():
        s = nat[nat["komoditas_id"] == cid].sort_values("tanggal")
        if s.empty:
            continue
        s25 = s[s["tahun"] == 2025]["harga_rp_per_kg"]
        s26 = s[s["tahun"] == 2026]["harga_rp_per_kg"]
        avg25, avg26 = s25.mean(), s26.mean()
        yoy = (avg26 - avg25) / avg25 * 100 if avg25 else None
        imax = s["harga_rp_per_kg"].idxmax()
        cv = s["harga_rp_per_kg"].std() / s["harga_rp_per_kg"].mean() * 100
        com_stats[cid] = {
            "nama": cname, "n_hari": len(s),
            "rata2025": round(avg25), "rata2026": round(avg26),
            "yoy_pct": round(yoy, 1) if yoy is not None else None,
            "maks": int(s.loc[imax, "harga_rp_per_kg"]),
            "tgl_maks": str(s.loc[imax, "tanggal"].date()),
            "minimum": int(s["harga_rp_per_kg"].min()),
            "cv_pct": round(cv, 1),
        }
    findings["komoditas"] = com_stats

    # ---------- per-group national stats ----------
    grp_stats = {}
    for gname, cids in GROUPS.items():
        s = nat[nat["komoditas_id"].isin(cids)].sort_values("tanggal")
        # group index: mean across commodities per day (then stats on that index)
        daily = s.groupby("tanggal")["harga_rp_per_kg"].mean()
        d25 = s[s["tahun"] == 2025]["harga_rp_per_kg"].mean()
        d26 = s[s["tahun"] == 2026]["harga_rp_per_kg"].mean()
        yoy = (d26 - d25) / d25 * 100
        cv = daily.std() / daily.mean() * 100
        imax = daily.idxmax()
        grp_stats[gname] = {
            "rata2025": round(d25), "rata2026": round(d26),
            "yoy_pct": round(yoy, 1), "cv_pct": round(cv, 1),
            "indeks_maks": round(daily.max()),
            "tgl_indeks_maks": str(imax.date()),
            "komoditas": cids,
        }
    findings["kelompok"] = grp_stats

    # ---------- province disparities (2026 avg per group) ----------
    prov_stats = {}
    for gname, cids in GROUPS.items():
        p = prov[(prov["komoditas_id"].isin(cids)) & (prov["tahun"] == 2026)]
        byprov = p.groupby("provinsi")["harga_rp_per_kg"].mean().sort_values()
        termurah, termahal = byprov.index[0], byprov.index[-1]
        gap = (byprov.iloc[-1] - byprov.iloc[0]) / byprov.iloc[0] * 100
        prov_stats[gname] = {
            "termurah": {"provinsi": termurah, "rata": round(byprov.iloc[0])},
            "termahal": {"provinsi": termahal, "rata": round(byprov.iloc[-1])},
            "selisih_pct": round(gap, 1),
            "top5_mahal": [(i, round(v)) for i, v in byprov.tail(5).iloc[::-1].items()],
            "top5_murah": [(i, round(v)) for i, v in byprov.head(5).items()],
        }
    findings["provinsi"] = prov_stats

    # ---------- Ramadan / Lebaran effects ----------
    ram = {}
    for gname, cids in GROUPS.items():
        rows = []
        for rs, re_ in RAMADAN:
            win = nat[(nat["komoditas_id"].isin(cids)) & (nat["tanggal"] >= rs) & (nat["tanggal"] <= re_)]
            pre = nat[(nat["komoditas_id"].isin(cids)) & (nat["tanggal"] >= str(pd.Timestamp(rs) - pd.Timedelta(days=30))) & (nat["tanggal"] < rs)]
            post = nat[(nat["komoditas_id"].isin(cids)) & (nat["tanggal"] > re_) & (nat["tanggal"] <= str(pd.Timestamp(re_) + pd.Timedelta(days=30)))]
            rows.append({"periode": f"Ramadan {rs[:4]}",
                         "sebelum": round(pre["harga_rp_per_kg"].mean()) if len(pre) else None,
                         "selama": round(win["harga_rp_per_kg"].mean()) if len(win) else None,
                         "sesudah": round(post["harga_rp_per_kg"].mean()) if len(post) else None})
        ram[gname] = rows
    findings["ramadan"] = ram

    # ---------- cross-commodity ----------
    yoy_sorted = sorted(((g, v["yoy_pct"]) for g, v in grp_stats.items()), key=lambda x: -x[1])
    cv_sorted = sorted(((COM_NAMES[c], v["cv_pct"]) for c, v in com_stats.items()), key=lambda x: -x[1])
    findings["lintas_komoditas"] = {
        "yoy_tertinggi": {"kelompok": yoy_sorted[0][0], "pct": yoy_sorted[0][1]},
        "yoy_terendah": {"kelompok": yoy_sorted[-1][0], "pct": yoy_sorted[-1][1]},
        "paling_volatil": {"komoditas": cv_sorted[0][0], "cv_pct": cv_sorted[0][1]},
        "paling_stabil": {"komoditas": cv_sorted[-1][0], "cv_pct": cv_sorted[-1][1]},
    }

    with open(f"{ROOT}/findings.json", "w") as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    print("findings.json written")

    # ================= CHARTS =================
    # 1. Tren nasional 4 kelompok
    fig, ax = plt.subplots(figsize=(11, 5.2))
    for i, (gname, cids) in enumerate(GROUPS.items()):
        s = nat[nat["komoditas_id"].isin(cids)]
        daily = s.groupby("tanggal")["harga_rp_per_kg"].mean()
        ax.plot(daily.index, daily.values, label=gname, color=PAL[i], lw=1.6)
    for rs, re_ in RAMADAN:
        ax.axvspan(pd.Timestamp(rs), pd.Timestamp(re_), color="gray", alpha=0.08)
    ax.set_title("Tren Harga Pangan Nasional 2025-2026 (rata-rata per kelompok, Rp/kg)", fontsize=13, fontweight="bold", loc="left")
    ax.set_ylabel("Rp/kg")
    ax.legend(frameon=False, ncols=4, loc="upper left")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", ".")))
    fig.tight_layout(); fig.savefig(f"{CHARTS}/01_tren_nasional.png", bbox_inches="tight"); plt.close(fig)

    # 2. YoY per kelompok
    fig, ax = plt.subplots(figsize=(8, 4.4))
    names = list(grp_stats.keys()); vals = [grp_stats[g]["yoy_pct"] for g in names]
    bars = ax.bar(names, vals, color=[PAL_TEAL if v >= 0 else "#C1553B" for v in vals], width=0.55)
    ax.set_title("Perubahan Harga Rata-rata 2025 ke 2026 per Kelompok (%)", fontsize=13, fontweight="bold", loc="left")
    ax.set_ylabel("Persen (%)")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.05, f"{v:+.1f}%", ha="center", fontsize=10, fontweight="bold")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/02_yoy_kelompok.png", bbox_inches="tight"); plt.close(fig)

    # 3. Volatilitas per komoditas
    fig, ax = plt.subplots(figsize=(9, 5.4))
    items = sorted(com_stats.items(), key=lambda x: x[1]["cv_pct"])
    ax.barh([COM_NAMES[c] for c, _ in items], [v["cv_pct"] for _, v in items], color=PAL_TEAL, height=0.55)
    ax.set_title("Volatilitas Harga (Koefisien Variasi, %)", fontsize=13, fontweight="bold", loc="left")
    ax.set_xlabel("CV (%)")
    for i, (_, v) in enumerate(items):
        ax.text(v["cv_pct"] + 0.05, i, f"{v['cv_pct']}%", va="center", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{CHARTS}/03_volatilitas.png", bbox_inches="tight"); plt.close(fig)

    # 4. Puncak harga per kelompok
    fig, ax = plt.subplots(figsize=(9, 4.6))
    names = list(grp_stats.keys())
    maks = [grp_stats[g]["indeks_maks"] for g in names]
    tgls = [grp_stats[g]["tgl_indeks_maks"] for g in names]
    bars = ax.bar(names, maks, color=PAL[:4], width=0.55)
    ax.set_title("Titik Tertinggi Indeks Harga per Kelompok (2025-2026)", fontsize=13, fontweight="bold", loc="left")
    ax.set_ylabel("Rp/kg (indeks rata-rata)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", ".")))
    for b, m, t in zip(bars, maks, tgls):
        ax.text(b.get_x() + b.get_width()/2, b.get_height(), f"{rp(m)}\n{t}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{CHARTS}/04_puncak.png", bbox_inches="tight"); plt.close(fig)

    # 5. Disparitas provinsi per kelompok
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, (gname, _) in zip(axes.flat, GROUPS.items()):
        st = prov_stats[gname]
        labs = [f"{p}\n({rp(v)})" for p, v in st["top5_murah"]] + [f"{p}\n({rp(v)})" for p, v in st["top5_mahal"]]
        vals = [v for _, v in st["top5_murah"]] + [v for _, v in st["top5_mahal"]]
        cols = [PAL_TEAL]*5 + ["#C1553B"]*5
        ax.barh(labs, vals, color=cols, height=0.6)
        ax.set_title(f"{gname} — 5 termurah vs 5 termahal (rata 2026)", fontsize=11, fontweight="bold", loc="left")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}rb"))
    fig.tight_layout(); fig.savefig(f"{CHARTS}/05_disparitas_provinsi.png", bbox_inches="tight"); plt.close(fig)

    # 6. Efek Ramadan
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, (gname, rows) in zip(axes.flat, ram.items()):
        x = np.arange(len(rows)); w = 0.22
        for j, lbl in enumerate(["sebelum", "selama", "sesudah"]):
            vals = [r[lbl] for r in rows]
            ax.bar(x + (j-1)*w, vals, width=w, label=lbl.capitalize(), color=PAL[j])
        ax.set_xticks(x); ax.set_xticklabels([r["periode"] for r in rows])
        ax.set_title(f"{gname}: harga sebelum/selama/sesudah Ramadan", fontsize=11, fontweight="bold", loc="left")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}rb"))
        ax.legend(frameon=False, fontsize=9)
    fig.tight_layout(); fig.savefig(f"{CHARTS}/06_ramadan.png", bbox_inches="tight"); plt.close(fig)

    # 7. Beras: 6 kualitas
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, cid in enumerate(GROUPS["Beras"]):
        s = nat[nat["komoditas_id"] == cid].sort_values("tanggal")
        ax.plot(s["tanggal"], s["harga_rp_per_kg"], label=COM_NAMES[cid].replace("Beras ", ""), color=PAL[i % len(PAL)], lw=1.4)
    ax.set_title("Harga Beras Nasional per Kualitas 2025-2026 (Rp/kg)", fontsize=13, fontweight="bold", loc="left")
    ax.set_ylabel("Rp/kg"); ax.legend(frameon=False, ncols=3, fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", ".")))
    fig.tight_layout(); fig.savefig(f"{CHARTS}/07_beras.png", bbox_inches="tight"); plt.close(fig)

    # 8. Minyak goreng: curah vs kemasan
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, cid in enumerate(GROUPS["Minyak Goreng"]):
        s = nat[nat["komoditas_id"] == cid].sort_values("tanggal")
        ax.plot(s["tanggal"], s["harga_rp_per_kg"], label=COM_NAMES[cid].replace("Minyak Goreng ", ""), color=PAL[i], lw=1.6)
    ax.set_title("Harga Minyak Goreng Nasional 2025-2026 (Rp/kg)", fontsize=13, fontweight="bold", loc="left")
    ax.set_ylabel("Rp/kg"); ax.legend(frameon=False)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", ".")))
    fig.tight_layout(); fig.savefig(f"{CHARTS}/08_minyak_goreng.png", bbox_inches="tight"); plt.close(fig)

    # 9. Gula pasir
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, cid in enumerate(GROUPS["Gula Pasir"]):
        s = nat[nat["komoditas_id"] == cid].sort_values("tanggal")
        ax.plot(s["tanggal"], s["harga_rp_per_kg"], label=COM_NAMES[cid].replace("Gula Pasir ", ""), color=PAL[i], lw=1.6)
    ax.set_title("Harga Gula Pasir Nasional 2025-2026 (Rp/kg)", fontsize=13, fontweight="bold", loc="left")
    ax.set_ylabel("Rp/kg"); ax.legend(frameon=False)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", ".")))
    fig.tight_layout(); fig.savefig(f"{CHARTS}/09_gula_pasir.png", bbox_inches="tight"); plt.close(fig)

    # 10. Daging sapi
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, cid in enumerate(GROUPS["Daging Sapi"]):
        s = nat[nat["komoditas_id"] == cid].sort_values("tanggal")
        ax.plot(s["tanggal"], s["harga_rp_per_kg"], label=COM_NAMES[cid].replace("Daging Sapi ", ""), color=PAL[i], lw=1.6)
    ax.set_title("Harga Daging Sapi Nasional 2025-2026 (Rp/kg)", fontsize=13, fontweight="bold", loc="left")
    ax.set_ylabel("Rp/kg"); ax.legend(frameon=False)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", ".")))
    fig.tight_layout(); fig.savefig(f"{CHARTS}/10_daging_sapi.png", bbox_inches="tight"); plt.close(fig)

    # 11. Boxplot distribusi 2026 per kelompok
    fig, ax = plt.subplots(figsize=(9, 5))
    data = [nat[(nat["komoditas_id"].isin(cids)) & (nat["tahun"] == 2026)]["harga_rp_per_kg"].values for cids in GROUPS.values()]
    bp = ax.boxplot(data, tick_labels=list(GROUPS.keys()), patch_artist=True)
    for p, c in zip(bp["boxes"], PAL[:4]):
        p.set_facecolor(c); p.set_alpha(0.7)
    ax.set_title("Sebaran Harga Nasional 2026 per Kelompok (Rp/kg)", fontsize=13, fontweight="bold", loc="left")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}rb"))
    fig.tight_layout(); fig.savefig(f"{CHARTS}/11_distribusi.png", bbox_inches="tight"); plt.close(fig)

    # 12. Rata-rata 2026 per provinsi: Beras (contoh kelompok terbesar)
    fig, ax = plt.subplots(figsize=(10, 12))
    p = prov[(prov["komoditas_id"].isin(GROUPS["Beras"])) & (prov["tahun"] == 2026)]
    byprov = p.groupby("provinsi")["harga_rp_per_kg"].mean().sort_values()
    ax.barh(byprov.index, byprov.values, color=PAL_TEAL, height=0.6)
    ax.set_title("Rata-rata Harga Beras 2026 per Provinsi (Rp/kg)", fontsize=13, fontweight="bold", loc="left")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", ".")))
    fig.tight_layout(); fig.savefig(f"{CHARTS}/12_beras_provinsi.png", bbox_inches="tight"); plt.close(fig)

    print("12 charts written")


if __name__ == "__main__":
    main()
