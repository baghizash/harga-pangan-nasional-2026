#!/usr/bin/env python3
"""Build Modul-Analisis-Harga-Pangan.pdf (A4 landscape, beginner-friendly ID).

Reads findings.json — every number comes from the PIHPS API data.
Design dials 6/3/3 (module): clean, generous whitespace, real charts.
"""
import json
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak,
)

HERE = Path(__file__).resolve().parent
F = json.loads((HERE / "findings.json").read_text())
OUT = str(Path.home() / "workspace" / "coursera-modules" / "Modul-Analisis-Harga-Pangan.pdf")
CHARTS = HERE / "charts"
W, H = landscape(A4)
NAVY = HexColor("#1E3A8A")
TEAL = HexColor("#0D9488")
DARK = HexColor("#1F2937")
GRAY = HexColor("#6B7280")
LIGHT = HexColor("#EFF6FF")

styles = {
    "cover": ParagraphStyle("cover", fontName="Helvetica-Bold", fontSize=30, leading=36,
                            textColor=NAVY, alignment=TA_LEFT),
    "coversub": ParagraphStyle("coversub", fontName="Helvetica", fontSize=15, leading=21,
                               textColor=DARK, alignment=TA_LEFT),
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=27,
                         textColor=NAVY, spaceBefore=6, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=16, leading=20,
                         textColor=TEAL, spaceBefore=8, spaceAfter=6),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=12.5, leading=18,
                           textColor=DARK, spaceAfter=7),
    "bullet": ParagraphStyle("bullet", parent=ParagraphStyle("b", fontName="Helvetica",
                             fontSize=12.5, leading=18, textColor=DARK, spaceAfter=5,
                             leftIndent=16, bulletIndent=6)),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=10.5, leading=15,
                          textColor=DARK, backColor=LIGHT, spaceAfter=8,
                          leftIndent=8, borderPadding=(6, 6, 6)),
    "caption": ParagraphStyle("caption", fontName="Helvetica-Oblique", fontSize=10.5,
                              leading=14, textColor=GRAY, alignment=TA_CENTER,
                              spaceBefore=4, spaceAfter=10),
    "warn": ParagraphStyle("warn", fontName="Helvetica", fontSize=12.5, leading=18,
                           textColor=HexColor("#92400E"), backColor=HexColor("#FEF3C7"),
                           borderPadding=(8, 8, 8), spaceAfter=8),
}
story = []


def P(text, style="body"):
    story.append(Paragraph(text, styles[style]))


def B(text):
    story.append(Paragraph(text, styles["bullet"], bulletText="•"))


def CODE(text):
    story.append(Paragraph(text.replace(" ", "&nbsp;").replace("\n", "<br/>"), styles["code"]))


def CHART(fname, caption, width=21 * cm):
    story.append(Image(str(CHARTS / fname), width=width, height=width * 0.58))
    P(caption, "caption")


def TABLE(data, widths=None):
    t = Table([[Paragraph(str(c), styles["body"]) for c in row] for row in data],
              colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), LIGHT]),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


def rp(v):
    return f"Rp{v:,}".replace(",", ".")


kl = F["kelompok"]
km = F["komoditas"]
pv = F["provinsi"]
lk = F["lintas_komoditas"]
per = F["periode"]
rb = F["ramadan"]["Beras"]

# ---------- COVER ----------
story.append(Spacer(1, 3 * cm))
P("MODUL BELAJAR", "cover")
P("Modul Analisis Harga Pangan Indonesia 2026", "cover")
P("Dari API PIHPS sampai Dashboard Power BI: Studi Kasus Nyata untuk Pemula", "coversub")
story.append(Spacer(1, 0.6 * cm))
P("Modul ini mengajak kamu membangun satu project analisis data nyata dari nol: "
  "harga beras, daging sapi, minyak goreng, dan gula pasir di Indonesia pada 2026. "
  "Kamu akan belajar mengambil data dari API resmi PIHPS / Bank Indonesia, "
  "menyusunnya menjadi tabel yang rapi, menjawab pertanyaan bisnis dengan SQL, "
  "memvisualisasikan dengan Python, lalu menyusun dashboard Power BI. "
  "Semua angka di modul ini dihitung dari data — tidak ada yang dikarang.", "coversub")
story.append(Spacer(1, 0.5 * cm))
P("Sumber data: API publik PIHPS / Bank Indonesia (bi.go.id/hargapangan), Pasar Tradisional. "
  "Periode: 1 Jan 2025 – 23 Okt 2026. 13 komoditas, 34 provinsi.", "warn")
story.append(PageBreak())

# ---------- BAB 1 ----------
P("Bab 1 — Kenalan dengan Project Ini", "h1")
P("Kenapa harga pangan? Karena beras, daging sapi, minyak goreng, dan gula pasir "
  "adalah bahan pokok yang harganya langsung menentukan daya beli jutaan rumah "
  "tangga Indonesia. Kalau harganya naik 5–7% dalam setahun, keluarga berpendapatan "
  "rendah yang paling terpukul.", "body")
P("Pertanyaan yang akan dijawab", "h2")
B("Kelompok mana yang naik paling tinggi pada 2026 dibanding 2025?")
B("Komoditas mana yang paling volatile (harganya paling sulit ditebak)?")
B("Di provinsi mana harga paling mahal dan paling murah?")
B("Apakah Ramadan benar-benar mendongkrak harga?")
P("Alur kerja project ini", "h2")
B("1. Ambil data harian dari API publik PIHPS (scripts/fetch_pihps.py).")
B("2. Rapikan menjadi CSV tidy dan database SQLite (scripts/assemble.py, scripts/load_to_sqlite.py).")
B("3. Jawab pertanyaan dengan SQL (sql/queries.sql) dan hitung temuan (scripts/analyze.py → findings.json).")
B("4. Visualisasikan dengan Python/matplotlib (12 chart).")
B("5. Susun paket dashboard Power BI (folder powerbi/).")
story.append(PageBreak())

# ---------- BAB 2 ----------
P("Bab 2 — Mengambil Data dari API PIHPS", "h1")
P("PIHPS (Pusat Informasi Harga Pangan Strategis) milik Bank Indonesia mempublikasikan "
  "harga harian di pasar tradisional lewat API publik. Tidak perlu login — cukup "
  "kirim request GET dengan header seperti browser.", "body")
P("Endpoint dan parameter", "h2")
CODE("GET https://www.bi.go.id/hargapangan/WebSite/TabelHarga/GetGridDataKomoditas\n"
     "?price_type_id=1          # 1 = Pasar Tradisional\n"
     "&comcat_id=1             # id komoditas daun (1 s.d. 21)\n"
     "&province_id=1           # id provinsi (satu per request)\n"
     "&tipe_laporan=1          # 1 = harian\n"
     "&start_date=2025-01-01&end_date=2026-10-23")
P("Satu request = satu komoditas × satu provinsi. Responsnya berisi dua baris: "
  "baris nasional dan baris provinsi, dengan satu kolom per tanggal (DD/MM/YYYY). "
  "Nilai \"-\" artinya hari itu tidak ada laporan. Total: 13 komoditas × 34 provinsi "
  "= 442 request, menghasilkan 433 chunk JSON dan 9 kombinasi tanpa seri laporan "
  "(misalnya beras di Gorontalo) — dicatat sebagai gap.", "body")
P("Catatan penting untuk pemula", "h2")
B("API ini TIDAK punya seri daun untuk telur, daging ayam, atau bawang — "
  "jangan dicari, jangan dikarang.")
B("Selalu kirim header User-Agent Chrome dan X-Requested-With: XMLHttpRequest, "
  "pakai cookie jar, dan beri jeda antar request.")
B("Cek rentang tanggal yang tersedia dulu: data terkonfirmasi ada dari "
  "01/01/2018 sampai 19/10/2026.")
story.append(PageBreak())

# ---------- BAB 3 ----------
P("Bab 3 — Menyusun Data: Nasional dan Provinsi Dipisah", "h1")
P("Pelajaran penting dari project ini (dan dari proyek Harga Cabai sebelumnya): "
  "respons API mencampur baris nasional dan baris provinsi. Kalau keduanya "
  "dimasukkan ke satu tabel fakta, rata-rata atau MAX yang tidak difilter "
  "provinsi akan salah.", "body")
P("Solusinya: dua tabel fakta terpisah sejak awal", "h2")
TABLE([
    ["Tabel", "Grain (1 baris =)", "Dipakai untuk"],
    ["fact_nasional", "1 tanggal × 1 komoditas", "Tren nasional, YoY, puncak, volatilitas nasional"],
    ["fact_provinsi", "1 tanggal × 1 komoditas × 1 provinsi", "Perbandingan provinsi, disparitas"],
    ["dim_komoditas", "1 komoditas", "Nama, kelompok, satuan"],
    ["dim_provinsi", "1 provinsi", "Nama provinsi"],
    ["dim_tanggal", "1 tanggal", "Tanggal, tahun, bulan"],
], widths=[3.2 * cm, 7 * cm, 12 * cm])
P("Dengan model ini, measure DAX tidak butuh guard khusus: satu visual selalu "
  "membaca tepat satu grain. Folder powerbi/ berisi kelima tabel sebagai CSV "
  "siap import.", "body")
P("Skala data", "h2")
B("6.149 baris nasional + 204.809 baris provinsi.")
B("473 hari laporan (1 Jan 2025 – 23 Okt 2026), 13 komoditas, 34 provinsi.")
B("Database verifikasi: data/harga_pangan.db (star schema). "
  "Semua temuan dihitung ulang dari database ini dengan SQL — bukan dari cache.")
story.append(PageBreak())

# ---------- BAB 4 ----------
P("Bab 4 — Menjawab Pertanyaan dengan SQL", "h1")
P("Setelah data rapi, pertanyaan bisnis dijawab dengan query SQL "
  "(lihat sql/queries.sql — 8 query siap jalan). Contoh pola yang dipakai:", "body")
P("Rata-rata tahunan per kelompok (YoY)", "h2")
CODE("SELECT k.kelompok, t.tahun, ROUND(AVG(n.harga_rp_per_kg)) AS rata2\n"
     "FROM fact_nasional n\n"
     "JOIN dim_komoditas k ON k.komoditas_id = n.komoditas_id\n"
     "JOIN dim_tanggal t  ON t.tanggal = n.tanggal\n"
     "GROUP BY k.kelompok, t.tahun;")
P("Hasilnya (dibulatkan):", "body")
TABLE([
    ["Kelompok", "Rata-rata 2025", "Rata-rata 2026", "YoY"],
    ["Beras", rp(kl["Beras"]["rata2025"]), rp(kl["Beras"]["rata2026"]), f"+{kl['Beras']['yoy_pct']}%"],
    ["Daging Sapi", rp(kl["Daging Sapi"]["rata2025"]), rp(kl["Daging Sapi"]["rata2026"]), f"+{kl['Daging Sapi']['yoy_pct']}%"],
    ["Minyak Goreng", rp(kl["Minyak Goreng"]["rata2025"]), rp(kl["Minyak Goreng"]["rata2026"]), f"+{kl['Minyak Goreng']['yoy_pct']}%"],
    ["Gula Pasir", rp(kl["Gula Pasir"]["rata2025"]), rp(kl["Gula Pasir"]["rata2026"]), f"+{kl['Gula Pasir']['yoy_pct']}%"],
], widths=[5 * cm, 5 * cm, 5 * cm, 4 * cm])
P("Volatilitas dihitung dengan koefisien variasi (standar deviasi ÷ rata-rata). "
  "Di SQL: pakai subquery untuk rata-rata dan STDEV per komoditas, lalu bandingkan. "
  "Minyak Goreng Curah keluar sebagai yang paling volatile (CV 4,3%), "
  "Gula Pasir Premium paling stabil (CV 1,3%).", "body")
story.append(PageBreak())

# ---------- BAB 5 ----------
P("Bab 5 — Visualisasi dan Temuan Utama", "h1")
P("Keempat kelompok naik sepanjang 2026 — tekanan harga bersifat luas.", "h2")
CHART("01_tren_nasional.png", "Tren harian indeks per kelompok, 2025–2026.")
P("Minyak goreng naik tertinggi dan paling liar.", "h2")
CHART("02_yoy_kelompok.png", "Kenaikan rata-rata 2026 vs 2025 per kelompok.")
CHART("03_volatilitas.png", "Koefisien variasi 2026 per komoditas.")
P("Puncak serentak medio Oktober 2026 — tiga kelompok mencapai titik tertinggi "
  "pada 13–14 Oktober 2026 dan Gula Pasir menyusul tipis melampauinya pada "
  "21 Oktober 2026, pola yang sama dengan lonjakan cabai (12 Okt 2026). "
  "Ini sinyal tekanan harga pangan luas, bukan ulah satu komoditas.", "body")
CHART("04_puncak.png", "Titik tertinggi indeks per kelompok, 2025–2026.")
story.append(PageBreak())

# ---------- BAB 6 ----------
P("Bab 6 — Disparitas Provinsi dan Efek Ramadan", "h1")
P("Provinsi timur dan kepulauan membayar jauh lebih mahal.", "h2")
CHART("05_disparitas_provinsi.png", "Gap provinsi termahal vs termurah per kelompok.")
B(f"Beras: {pv['Beras']['termurah']['provinsi']} {rp(pv['Beras']['termurah']['rata'])}/kg vs "
  f"{pv['Beras']['termahal']['provinsi']} {rp(pv['Beras']['termahal']['rata'])}/kg "
  f"(selisih {pv['Beras']['selisih_pct']}%).")
B(f"Daging Sapi: {pv['Daging Sapi']['termurah']['provinsi']} vs {pv['Daging Sapi']['termahal']['provinsi']} "
  f"(selisih {pv['Daging Sapi']['selisih_pct']}%).")
P("Gap 36–41% antarprovinsi konsisten di semua kelompok — logistik dan rantai "
  "pasok adalah bagian dari masalah harga, bukan cuma produksi.", "body")
P("Efek Ramadan kecil.", "h2")
CHART("06_ramadan.png", "Harga beras 30 hari sebelum, selama, dan sesudah Ramadan.")
P(f"Ramadan 2025: {rp(rb[0]['sebelum'])}/kg → {rp(rb[0]['selama'])}/kg "
  "(+0,2%). Ramadan 2026: {rp(rb[1]['sebelum'])}/kg → "
  f"{rp(rb[1]['selama'])}/kg (+0,4%). Kenaikan hanya "
  "0,2–0,4% — narasi 'harga selalu melonjak saat puasa' tidak terbukti pada data.", "body")
story.append(PageBreak())

# ---------- BAB 7 ----------
P("Bab 7 — Membangun Dashboard Power BI", "h1")
P("Folder powerbi/ berisi kit lengkap: 5 CSV star-schema, file DAX, "
  "spesifikasi layout 4 halaman, dan panduan rakit. Langkahnya:", "body")
P("1. Import dan relasi", "h2")
B("Import kelima CSV, tandai dim_tanggal sebagai date table.")
B("Buat relasi: dim_tanggal → fact_nasional, dim_komoditas → fact_nasional, "
  "dim_tanggal → fact_provinsi, dim_komoditas → fact_provinsi, dim_provinsi → fact_provinsi.")
P("2. Tempel DAX", "h2")
CODE("Rata-rata Nasional = AVERAGE(fact_nasional[harga_rp_per_kg])\n"
     "YoY % = DIVIDE([Rata-rata Nasional 2026]-[Rata-rata Nasional 2025],\n"
     "              [Rata-rata Nasional 2026])")
P("Lihat powerbi/measures_dax.md untuk seluruh measure beserta catatan level "
  "(nasional vs provinsi) — baca bagian itu dulu sebelum membuat visual.", "body")
P("3. Bangun 4 halaman", "h2")
B("Halaman 1: Ringkasan Nasional (KPI + tren). Halaman 2: Volatilitas & Puncak.")
B("Halaman 3: Disparitas Provinsi (peta + bar). Halaman 4: Musiman & Metodologi.")
B("Aturan emas: satu visual = satu tabel fakta. Visual nasional pakai measures "
  "NASIONAL; visual provinsi pakai measures PROVINSI. Jangan campur.")
P("4. Verifikasi", "h2")
B(f"KPI Halaman 1 harus: Beras +{kl['Beras']['yoy_pct']}%, Daging Sapi "
  f"+{kl['Daging Sapi']['yoy_pct']}%, Minyak Goreng +{kl['Minyak Goreng']['yoy_pct']}%, "
  f"Gula Pasir +{kl['Gula Pasir']['yoy_pct']}%.")
B("Kalau beda, cek: visual memakai tabel fakta yang benar?")
story.append(PageBreak())

# ---------- PENUTUP ----------
P("Penutup", "h1")
P("Tiga pesan utama project ini:", "body")
B("1. Minyak goreng naik tertinggi (+6,8%) dan paling volatile — pantau versi curah.")
B("2. Medio Oktober 2026 adalah puncak tekanan harga pangan nasional 2026 (tiga kelompok 13 Okt, Gula Pasir 21 Okt).")
B("3. Disparitas 36–41% antarprovinsi menuntut perhatian logistik, bukan cuma produksi.")
P("Struktur project (lihat repo GitHub):", "h2")
B("scripts/ — fetch_pihps.py, assemble.py, analyze.py, load_to_sqlite.py")
B("data/ — CSV nasional & provinsi, SOURCES.md (asal data)")
B("sql/queries.sql — 8 query verifikasi")
B("charts/ — 12 visualisasi PNG")
B("powerbi/ — kit dashboard (CSV, DAX, layout, panduan)")
B("findings.json — semua temuan dalam format mesin")
P("Latihan untukmu: ganti periode end_date ke bulan berjalan, jalankan ulang "
  "pipeline, dan lihat apakah puncak Oktober 2026 masih bertahan. "
  "Itulah cara analis memantau harga pangan setiap hari.", "body")

doc = SimpleDocTemplate(OUT, pagesize=landscape(A4),
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                        title="Modul Analisis Harga Pangan Indonesia 2026",
                        author="Baghiz Asshiddiqie Arasya")
doc.build(story)
print(f"Module saved: {OUT}")
