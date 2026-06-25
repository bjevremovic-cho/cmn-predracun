# -*- coding: utf-8 -*-
import os, json, re, textwrap
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
FONT_DIR   = os.path.join(BASE_DIR, 'static', 'fonts')
IMG_DIR    = os.path.join(BASE_DIR, 'static', 'img')
LOGO_PATH  = os.path.join(IMG_DIR,  'logo.png')
PECAT_PATH = os.path.join(IMG_DIR,  'pecat.png')
FONT_REG   = os.path.join(FONT_DIR, 'DejaVuSans.ttf')
FONT_BOLD  = os.path.join(FONT_DIR, 'DejaVuSans-Bold.ttf')
FONT_IT    = os.path.join(FONT_DIR, 'DejaVuSans-Oblique.ttf')
FONT_BI    = os.path.join(FONT_DIR, 'DejaVuSans-BoldOblique.ttf')

MOJA_FIRMA = {
    "naziv":     "CENTAR ZA MENADŽMENT D.O.O. Beograd",
    "adresa":    "Hercegovačka 15, 11000 Beograd",
    "pib":       "109907347",
    "mb":        "21265233",
    "racun":     "205-242588-18",
    "email":     "office@cmn.rs",
    "potpisnik": "Nikola Živančević",
}

def fmt_br(x):
    try:
        s = "{:,.2f}".format(float(x))
        return s.replace(",","X").replace(".",",").replace("X",".")
    except:
        return "0,00"

def fmt_datum(t):
    if not t: return ""
    s = str(t).strip()
    if not s or s.lower() == 'nan': return ""
    s = re.sub(r'\.0$', '', s)
    for fmt in ("%d.%m.%Y.", "%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%d.%m.%Y.")
        except:
            pass
    return s if s.endswith('.') else s + '.'

def generi_pdf(predracun: dict) -> bytes:
    stavke = predracun.get('stavke', [])
    if isinstance(stavke, str):
        try:
            stavke = json.loads(stavke)
        except:
            stavke = []

    osnov = 0.0; pdv_total = 0.0
    for st in stavke:
        try:
            c = float(st.get('cena', 0)); k = float(st.get('kolicina', 1)); p = float(st.get('pdv', 20))
            b = c * k; osnov += b; pdv_total += b * p / 100
        except: pass
    ukupno = osnov + pdv_total

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(18, 15, 18)
    pdf.add_page()
    pdf.add_font('R',  '', FONT_REG)
    pdf.add_font('B',  '', FONT_BOLD)
    pdf.add_font('I',  '', FONT_IT)
    pdf.add_font('BI', '', FONT_BI)

    W = 174; LM = 18

    # ── HEADER ────────────────────────────────────────────────────────────────
    # Logo left — VEĆI (h=26 umesto 18)
    logo_h = 34
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=LM, y=5, h=logo_h)

    # Firma desno
    pdf.set_xy(LM, 12)
    pdf.set_font('B', '', 11)
    pdf.cell(W, 6, MOJA_FIRMA['naziv'], align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('R', '', 8.5)
    pdf.set_x(LM)
    pdf.cell(W, 5, f"{MOJA_FIRMA['adresa']} | PIB: {MOJA_FIRMA['pib']} | MB: {MOJA_FIRMA['mb']}", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(LM)
    pdf.cell(W, 5, f"Račun: {MOJA_FIRMA['racun']} | Email: {MOJA_FIRMA['email']}", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Crta ispod headera
    pdf.set_y(max(pdf.get_y() + 2, 42))
    pdf.set_draw_color(150, 150, 150)
    pdf.set_line_width(0.5)
    pdf.line(LM, pdf.get_y(), LM + W, pdf.get_y())
    pdf.ln(5)

    # ── KUPAC ─────────────────────────────────────────────────────────────────
    kupac_naziv  = str(predracun.get('kupac_naziv', '')).strip()
    kupac_adresa = str(predracun.get('kupac_adresa', '')).strip()
    kupac_mesto  = str(predracun.get('kupac_mesto', '')).strip()
    kupac_pib    = str(predracun.get('kupac_pib', '')).replace('.0','').strip()
    kupac_mb     = str(predracun.get('kupac_mb', '')).replace('.0','').strip()
    kupac_jbkjs  = str(predracun.get('kupac_jbkjs', '')).replace('.0','').split('.')[0].strip()
    kupac_extra  = str(predracun.get('kupac_extra', '')).strip()
    for v in ('nan', 'None', '0', 'none'):
        if kupac_pib    == v: kupac_pib    = ''
        if kupac_mb     == v: kupac_mb     = ''
        if kupac_jbkjs  == v: kupac_jbkjs  = ''
        if kupac_adresa == v: kupac_adresa = ''
        if kupac_mesto  == v: kupac_mesto  = ''
        if kupac_extra  == v: kupac_extra  = ''

    pdf.set_font('B', '', 9)
    pdf.cell(W, 5.5, "KUPAC:", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('B', '', 10)
    pdf.cell(W, 6, kupac_naziv, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Adresa i mesto - prikaži samo ako postoje
    adresa_full = ', '.join(filter(None, [kupac_adresa, kupac_mesto]))
    if adresa_full:
        pdf.set_font('R', '', 9)
        pdf.cell(W, 5, adresa_full, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # PIB | MB | JBKJS
    pib_parts = []
    if kupac_pib:    pib_parts.append(f"PIB: {kupac_pib}")
    if kupac_mb:     pib_parts.append(f"MB: {kupac_mb}")
    if kupac_jbkjs:  pib_parts.append(f"JBKJS: {kupac_jbkjs}")
    if pib_parts:
        pdf.set_font('R', '', 9)
        pdf.cell(W, 5, " | ".join(pib_parts), align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Extra polje (npr. naziv organka) - POSLE PIB/MB/JBKJS, višeredni
    if kupac_extra:
        pdf.set_font('I', '', 9)
        pdf.multi_cell(W, 5, kupac_extra, align='R')

    # ── CRTA ISPOD KUPCA (pre PREDRAČUNA) ─────────────────────────────────────
    pdf.ln(4)
    pdf.set_draw_color(150, 150, 150)
    pdf.set_line_width(0.5)
    pdf.line(LM, pdf.get_y(), LM + W, pdf.get_y())
    pdf.ln(6)

    # ── TITLE ─────────────────────────────────────────────────────────────────
    pdf.set_font('B', '', 20)
    broj = predracun.get('broj', '')
    pdf.cell(W, 10, f"PREDRAČUN br. {broj}", align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

    dizd = fmt_datum(predracun.get('datum_izd', ''))
    dval = fmt_datum(predracun.get('datum_val', ''))
    pdf.set_font('R', '', 9.5)
    datum_line = ""
    if dizd: datum_line += f"Datum izdavanja: {dizd}"
    if dval: datum_line += f" | Datum valute: {dval}"
    if datum_line:
        pdf.cell(W, 6, datum_line, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    # ── DOGADJAJ ──────────────────────────────────────────────────────────────
    dog_naziv = str(predracun.get('dogadjaj_naziv', '')).strip()
    dog_datum = str(predracun.get('dogadjaj_datum', '')).strip()
    if dog_naziv:
        line = dog_naziv
        if dog_datum and dog_datum not in ('nan',''):
            line += f" {dog_datum}"
        pdf.set_font('BI', '', 10)
        pdf.multi_cell(W, 6, line, align='L')
        pdf.ln(2)

    # ── STAVKE TABLE ──────────────────────────────────────────────────────────
    cw = [75, 12, 24, 27, 12, 24]
    hdr = [("Naziv usluge",1), ("Kol.",1), ("Cena",1), ("Vrednost\nbez PDV-a",2), ("PDV %",1), ("Vrednost\nsa PDV-om",2)]

    pdf.set_fill_color(230, 230, 230)
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.3)
    pdf.set_font('B', '', 8.5)
    hdr_h = 10
    y0 = pdf.get_y()
    x_cur = LM
    for (h, lines_count), w in zip(hdr, cw):
        parts = h.split('\n')
        pdf.rect(x_cur, y0, w, hdr_h, 'DF')
        if len(parts) == 2:
            pdf.set_xy(x_cur, y0 + 1.5)
            pdf.cell(w, 3.5, parts[0], align='C')
            pdf.set_xy(x_cur, y0 + 5.5)
            pdf.cell(w, 3.5, parts[1], align='C')
        else:
            pdf.set_xy(x_cur, y0)
            pdf.cell(w, hdr_h, parts[0], align='C')
        x_cur += w
    pdf.set_xy(LM, y0 + hdr_h)

    pdf.set_font('R', '', 9)
    for st in stavke:
        naziv   = str(st.get('naziv', ''))
        kol     = int(float(st.get('kolicina', 1)))
        cena    = float(st.get('cena', 0))
        pdv_p   = float(st.get('pdv', 20))
        bez_pdv = cena * float(kol)
        sa_pdv  = bez_pdv * (1 + pdv_p / 100)

        line_h = 5.0
        chars_per_line = int(cw[0] / 2.1)
        wrapped = textwrap.wrap(naziv, chars_per_line) or ['']
        row_h = max(line_h * len(wrapped), 8)

        y_row = pdf.get_y()
        if y_row + row_h > pdf.page_break_trigger:
            pdf.add_page(); y_row = pdf.get_y()

        vals = [naziv, str(int(kol)), fmt_br(cena), fmt_br(bez_pdv), f"{int(pdv_p)}%", fmt_br(sa_pdv)]
        row_aligns = ['L','C','R','R','C','R']
        x_cur = LM
        for val, w, a in zip(vals, cw, row_aligns):
            pdf.rect(x_cur, y_row, w, row_h, 'D')
            if a == 'L':
                pdf.set_xy(x_cur + 1, y_row + 1)
                pdf.multi_cell(w - 2, line_h, val, border=0, align='L')
            else:
                pdf.set_xy(x_cur, y_row)
                pdf.cell(w, row_h, val, border=0, align=a)
            x_cur += w
        pdf.set_xy(LM, y_row + row_h)

    pdf.ln(6)

    # ── PDV REKAPITULACIJA + UKUPNO ───────────────────────────────────────────
    y_rek = pdf.get_y()

    # Levo: rekapitulacija
    pdf.set_font('B', '', 9)
    pdf.cell(W, 5, "Rekapitulacija PDV-a", align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('B', '', 8.5)
    rek_cw = [18, 30, 24]
    pdf.set_fill_color(230, 230, 230)
    for h, w in zip(["Stopa","Osnovica","PDV"], rek_cw):
        pdf.cell(w, 6, h, border=1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.ln()

    pdv_groups = {}
    for st in stavke:
        try:
            c=float(st.get('cena',0)); k=float(st.get('kolicina',1)); p=float(st.get('pdv',20))
            b=c*k
            if p not in pdv_groups: pdv_groups[p]={'osnov':0,'pdv':0}
            pdv_groups[p]['osnov']+=b; pdv_groups[p]['pdv']+=b*p/100
        except: pass

    pdf.set_font('R', '', 8.5)
    for rate, vals in pdv_groups.items():
        pdf.cell(rek_cw[0], 6, f"{int(rate)}%",      border=1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(rek_cw[1], 6, fmt_br(vals['osnov']),border=1, align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(rek_cw[2], 6, fmt_br(vals['pdv']),  border=1, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Desno: OSNOVICA / PDV / UKUPNO — bez crte pre UKUPNO
    right_x = LM + 88
    pdf.set_xy(right_x, y_rek + 5)
    pdf.set_font('R', '', 10)
    tot_lw = 52; tot_vw = 34

    pdf.set_x(right_x)
    pdf.cell(tot_lw, 7, "OSNOVICA:", align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(tot_vw, 7, fmt_br(osnov), align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(right_x)
    pdf.cell(tot_lw, 7, "PDV:", align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(tot_vw, 7, fmt_br(pdv_total), align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # UKUPNO — bez crte, samo bold tekst
    pdf.set_x(right_x)
    pdf.set_font('B', '', 11)
    pdf.cell(tot_lw, 9, "UKUPNO ZA NAPLATU (RSD):", align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(tot_vw, 9, fmt_br(ukupno), align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(8)

    # ── SPECIFIKACIJA (italic) ────────────────────────────────────────────────
    specifikacija = str(predracun.get('specifikacija', '')).strip()
    if specifikacija and specifikacija not in ('', 'nan', 'None'):
        pdf.set_font('I', '', 9)
        pdf.multi_cell(W, 5.5, specifikacija)
        pdf.ln(2)

    # ── NAPOMENA (sa predračuna - vidljiva na dokumentu) ──────────────────────
    # Čita napomena_predracun (ne evidencijsku napomenu)
    napomena = str(predracun.get('napomena_predracun', '') or predracun.get('napomena', '')).strip()
    if napomena and napomena not in ('', 'nan', 'None'):
        pdf.set_font('R', '', 9)
        pdf.multi_cell(W, 5.5, napomena)
        pdf.ln(3)

    # ── INSTRUKCIJE ZA PLAĆANJE ───────────────────────────────────────────────
    pdf.set_font('B', '', 9.5)
    pdf.cell(W, 6, "Instrukcije za plaćanje:", align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('R', '', 9)
    pdf.cell(W, 5.5, f"Primalac: {MOJA_FIRMA['naziv']} | Račun: {MOJA_FIRMA['racun']}", align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(W, 5.5, f"Poziv na broj: {broj}", align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    # ── POTPIS + PECAT ────────────────────────────────────────────────────────
    # Ime i firma PRVO, pa onda pečat ISPOD — ne pokriva tekst
    right_x2 = LM + W / 2
    pdf.set_font('B', '', 9.5)
    pdf.set_x(right_x2)
    pdf.cell(W / 2, 6, "Za Centar za menadžment d.o.o.", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(right_x2)
    pdf.cell(W / 2, 6, MOJA_FIRMA['potpisnik'], align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    # Pečat ISPOD teksta, veći (w=65 umesto 52)
    if os.path.exists(PECAT_PATH):
        pecat_w = 98
        pecat_x = LM + W - pecat_w
        pdf.image(PECAT_PATH, x=pecat_x, y=pdf.get_y(), w=pecat_w)

    return bytes(pdf.output())
