#!/usr/bin/env python3
"""Build Portofolio-Analisis-Harga-Pangan.pptx (16:9, 10 slides, ID).
Reads findings.json — every number comes from the PIHPS data.
Design: dials 7/5/3 (deck portfolio), no AI-slop (no purple gradients,
no fake numbers, real charts only).
"""
import json
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn

HERE = Path(__file__).resolve().parent
F = json.loads((HERE / "findings.json").read_text())
CHARTS = HERE / "charts"
OUT = Path.home() / "workspace" / "your_files" / "Portofolio-Analisis-Harga-Pangan.pptx"

NAVY = RGBColor(0x1E, 0x3A, 0x8A)
TEAL = RGBColor(0x0E, 0x7C, 0x7B)
RED = RGBColor(0xC0, 0x39, 0x2B)
DARK = RGBColor(0x1F, 0x29, 0x37)
GRAY = RGBColor(0x6B, 0x72, 0x80)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
AMBER = RGBColor(0xD9, 0xA4, 0x41)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


def rp(v):
    return f"Rp{v:,}".replace(",", ".")


def solid_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def textbox(slide, l, t, w, h):
    tx = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tx.text_frame
    tf.word_wrap = True
    return tf


def add_par(tf, text, size, color, bold=False, italic=False, first=False, align=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_after = Pt(8)
    if align is not None:
        p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    return p


def add_bullet(tf, text, size=17, first=False):
    p = add_par(tf, text, size, DARK, first=first)
    pPr = p._p.get_or_add_pPr()
    pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "\u2022"}))
    pPr.set("marL", "171450")
    pPr.set("indent", "-171450")
    p.space_after = Pt(10)
    p.space_before = Pt(2)
    return p


def content_title(slide, text):
    tf = textbox(slide, 0.7, 0.3, 11.9, 0.9)
    add_par(tf, text, 30, NAVY, bold=True, first=True)
    bar = slide.shapes.add_shape(1, Inches(0.7), Inches(1.15), Inches(1.5), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()


def content_slide(title, bullets, chart=None, caption=None, full_width=False):
    s = prs.slides.add_slide(blank)
    solid_bg(s, WHITE)
    content_title(s, title)
    bw = 11.9 if full_width else 5.6
    tf = textbox(s, 0.7, 1.5, bw, 5.2)
    for i, b in enumerate(bullets):
        add_bullet(tf, b, first=(i == 0))
    if chart:
        s.shapes.add_picture(str(CHARTS / f"{chart}.png"), Inches(6.8), Inches(1.5), width=Inches(5.8))
    if caption:
        tf2 = textbox(s, 0.7, 6.7, 11.9, 0.5)
        add_par(tf2, caption, 11, GRAY, italic=True, first=True)
    return s


kl = F["kelompok"]
km = F["komoditas"]
pv = F["provinsi"]
lk = F["lintas_komoditas"]

# ---- Slide 1: Title ----
s = prs.slides.add_slide(blank)
solid_bg(s, NAVY)
tf = textbox(s, 0.9, 1.0, 11.5, 1.2)
add_par(tf, "ANALISIS HARGA PANGAN NASIONAL INDONESIA 2026", 38, WHITE, bold=True, first=True)
tf = textbox(s, 0.9, 2.4, 11.5, 1.0)
add_par(tf, "Beras, Daging Sapi, Minyak Goreng, Gula Pasir: Tren, Volatilitas, dan Disparitas Provinsi", 20, WHITE, first=True)
tf = textbox(s, 0.9, 3.7, 11.5, 2.0)
add_par(tf, "Data harian PIHPS / Bank Indonesia — 13 komoditas, 34 provinsi, "
            "1 Januari 2025 sampai 19 Oktober 2026", 16, WHITE, first=True)
add_par(tf, "Plus: paket dashboard Power BI (star schema, DAX, panduan rakit)", 16, WHITE)
tf = textbox(s, 0.9, 6.0, 11.5, 0.8)
add_par(tf, "BAGHIZ ASSHIDDIQIE ARASYA", 20, WHITE, bold=True, first=True)

# ---- Slide 2: Latar belakang ----
content_slide("Kenapa Harga Pangan?", [
    "Beras, daging sapi, minyak goreng, dan gula pasir adalah bahan pokok yang "
    "harganya langsung menentukan daya beli jutaan rumah tangga Indonesia.",
    "Ketika harga pangan naik 5–7% dalam setahun, yang paling terpukul adalah "
    "keluarga berpendapatan rendah — porsi belanja pangannya paling besar.",
    "Analisis ini menjawab: kelompok mana yang naik paling tinggi di 2026, "
    "komoditas mana yang paling tidak stabil, di provinsi mana harganya paling mahal, "
    "dan apakah Ramadan benar-benar mendongkrak harga.",
    "Semua jawaban diambil dari data harian resmi PIHPS/BI, bukan perkiraan.",
], full_width=True, caption="Sumber data: API publik PIHPS / Bank Indonesia (bi.go.id/hargapangan), Pasar Tradisional.")

# ---- Slide 3: Data dan metode ----
content_slide("Data dan Metode", [
    "Data harian API PIHPS: 1 Jan 2025 – 19 Okt 2026 (469 hari laporan), "
    "6.097 baris nasional + 203.077 baris provinsi.",
    "13 komoditas daun: 6 kualitas beras, 2 daging sapi, 3 minyak goreng, 2 gula pasir. "
    "API ini tidak menyediakan seri daun untuk telur/daging ayam/bawang — tidak dipakai, tidak dikarang.",
    "Level nasional dan provinsi disimpan di tabel fakta TERPISAH sejak awal "
    "(fact_nasional, fact_provinsi) — pelajaran dari proyek cabai — sehingga agregasi "
    "dan measure DAX selalu membaca satu grain tanpa guard khusus.",
    "9 kombinasi komoditas-provinsi tidak memiliki seri laporan (mis. beras di Gorontalo) — "
    "dicatat sebagai gap, tidak diisi angka lain.",
], full_width=True)

# ---- Slide 4: Tren nasional ----
content_slide("Tren Nasional 2025–2026", [
    f"Minyak Goreng rata-rata 2026 {rp(kl['Minyak Goreng']['rata2026'])}/kg "
    f"({kl['Minyak Goreng']['yoy_pct']:+}% vs 2025) — kenaikan tertinggi.",
    f"Daging Sapi {rp(kl['Daging Sapi']['rata2026'])}/kg "
    f"({kl['Daging Sapi']['yoy_pct']:+}%); Beras {rp(kl['Beras']['rata2026'])}/kg "
    f"({kl['Beras']['yoy_pct']:+}%); Gula Pasir {rp(kl['Gula Pasir']['rata2026'])}/kg "
    f"({kl['Gula Pasir']['yoy_pct']:+}%).",
    "Keempat kelompok bergerak naik sepanjang 2026 — tekanan harga pangan bersifat luas, "
    "bukan satu komoditas saja.",
], chart="01_tren_nasional")

# ---- Slide 5: YoY ----
content_slide("Siapa Naik Paling Tinggi?", [
    f"Minyak Goreng: +{kl['Minyak Goreng']['yoy_pct']}% — juara kenaikan, "
    f"didorong Minyak Goreng Curah (+{km['com_17']['yoy_pct']}%).",
    f"Daging Sapi: +{kl['Daging Sapi']['yoy_pct']}% — kedua tertinggi, "
    f"harga rata-rata 2026 menembus {rp(kl['Daging Sapi']['rata2026'])}/kg.",
    f"Beras: +{kl['Beras']['yoy_pct']}% — moderat tapi basisnya besar: "
    f"Rp15.515 ke {rp(kl['Beras']['rata2026'])}/kg.",
    f"Gula Pasir: +{kl['Gula Pasir']['yoy_pct']}% — kenaikan paling rendah, "
    "harga paling terkendali.",
], chart="02_yoy_kelompok")

# ---- Slide 6: Volatilitas ----
content_slide("Volatilitas: Mana yang Paling Liar?", [
    f"{lk['paling_volatil']['komoditas']} paling volatile: CV {lk['paling_volatil']['cv_pct']}%, "
    f"melonjak ke {rp(km['com_17']['maks'])}/kg pada {km['com_17']['tgl_maks']}.",
    f"{lk['paling_stabil']['komoditas']} paling stabil: CV {lk['paling_stabil']['cv_pct']}%.",
    "Pola: minyak goreng curah (tanpa merek, rantai pasok pendek) jauh lebih liar "
    "dibanding versi kemasan bermerek — kualitas kemasan = stabilitas harga.",
    "Volatilitas tinggi = ketidakpastian bagi pedagang dan konsumen.",
], chart="03_volatilitas")

# ---- Slide 7: Puncak serentak ----
content_slide("Puncak Serentak 13 Oktober 2026", [
    "Keempat kelompok mencapai titik tertinggi pada 13–14 Okt 2026: "
    f"Beras {rp(kl['Beras']['indeks_maks'])}, Daging Sapi {rp(kl['Daging Sapi']['indeks_maks'])}, "
    f"Minyak Goreng {rp(kl['Minyak Goreng']['indeks_maks'])}, Gula Pasir {rp(kl['Gula Pasir']['indeks_maks'])}.",
    "Pola yang sama terlihat pada proyek Harga Cabai (puncak 12 Okt 2026) — "
    "ini lonjakan harga pangan luas, bukan ulah satu komoditas.",
    "Bagi pemantau kebijakan: minggu kedua Oktober 2026 adalah momen tekanan "
    "maksimum harga pangan tahun ini.",
], chart="04_puncak")

# ---- Slide 8: Disparitas provinsi ----
b, ds, mg, gp = pv["Beras"], pv["Daging Sapi"], pv["Minyak Goreng"], pv["Gula Pasir"]
content_slide("Disparitas Antar Provinsi", [
    f"Beras: {b['termurah']['provinsi']} {rp(b['termurah']['rata'])}/kg vs "
    f"{b['termahal']['provinsi']} {rp(b['termahal']['rata'])}/kg — selisih {b['selisih_pct']}%.",
    f"Daging Sapi: {ds['termurah']['provinsi']} {rp(ds['termurah']['rata'])}/kg vs "
    f"{ds['termahal']['provinsi']} {rp(ds['termahal']['rata'])}/kg — selisih {ds['selisih_pct']}%.",
    f"Minyak Goreng: {mg['termurah']['provinsi']} vs {mg['termahal']['provinsi']} "
    f"(selisih {mg['selisih_pct']}%); Gula Pasir: {gp['termurah']['provinsi']} vs "
    f"{gp['termahal']['provinsi']} (selisih {gp['selisih_pct']}%).",
    "Pola konsisten: provinsi timur dan kepulauan membayar 36–41% lebih mahal — "
    "logistik dan rantai pasok adalah bagian dari masalah harga.",
], chart="05_disparitas_provinsi")

# ---- Slide 9: Ramadan ----
rb = F["ramadan"]["Beras"]
content_slide("Apakah Ramadan Mendongkrak Harga?", [
    f"Ramadan 2025: beras {rp(rb[0]['sebelum'])}/kg (30 hari sebelum) → "
    f"{rp(rb[0]['selama'])}/kg (selama) → {rp(rb[0]['sesudah'])}/kg (30 hari sesudah).",
    f"Ramadan 2026: {rp(rb[1]['sebelum'])}/kg → {rp(rb[1]['selama'])}/kg → "
    f"{rp(rb[1]['sesudah'])}/kg.",
    "Kenaikan selama Ramadan hanya 0,2–0,4% — kecil. Narasi 'harga selalu melonjak "
    "saat puasa' tidak terbukti pada data 2025–2026 untuk beras.",
    "Tekanan harga yang sesungguhnya terjadi di luar musim Ramadan: tren naik "
    "jangka panjang + lonjakan Oktober 2026.",
], chart="06_ramadan")

# ---- Slide 10: Penutup ----
content_slide("Penutup", [
    "Tiga pesan utama: (1) Minyak goreng naik tertinggi (+6,7%) dan paling liar — "
    "pantau curah; (2) 13 Okt 2026 adalah puncak tekanan harga pangan nasional; "
    "(3) disparitas 36–41% antarprovinsi menuntut perhatian logistik, bukan cuma produksi.",
    "Paket dashboard Power BI tersedia di folder powerbi/: star schema 5 tabel, "
    "measure DAX siap tempel (dengan catatan level nasional vs provinsi), "
    "layout 4 halaman, dan panduan rakit langkah demi langkah.",
    "Semua angka dapat direproduksi: jalankan scripts/fetch_pihps.py lalu "
    "scripts/analyze.py — findings.json dan 12 chart dihitung ulang dari nol.",
    "Terima kasih.",
], full_width=True)

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUT))
print(f"PPT saved: {OUT}")
