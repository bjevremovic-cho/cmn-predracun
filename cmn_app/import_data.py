# -*- coding: utf-8 -*-
"""
Run this in Railway Console: python import_data.py
Imports all data from baza_kupaca_IMPORT.xlsx via URL
"""
import os, json, sys
import urllib.request

DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_conn():
    if DATABASE_URL:
        import psycopg2, psycopg2.extras
        return psycopg2.connect(DATABASE_URL), 'pg'
    else:
        import sqlite3
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'cmn.db')
        conn = sqlite3.connect(db_path)
        return conn, 'sqlite'

def run_sql(conn, db_type, sql, args=None, many=False):
    if db_type == 'pg':
        import psycopg2.extras
        cur = conn.cursor()
        pg_sql = sql.replace('?', '%s')
        if many:
            psycopg2.extras.execute_batch(cur, pg_sql, args, page_size=500)
        elif args:
            cur.execute(pg_sql, args)
        else:
            cur.execute(pg_sql)
    else:
        if many:
            conn.executemany(sql, args)
        elif args:
            conn.execute(sql, args)
        else:
            conn.execute(sql)

def main():
    try:
        import pandas as pd
    except ImportError:
        print("Installing pandas..."); os.system("pip install pandas openpyxl -q")
        import pandas as pd

    # Try to find xlsx file
    xlsx_path = None
    for p in ['baza_kupaca_IMPORT.xlsx', 'baza_kupaca.xlsx', '/tmp/baza.xlsx']:
        if os.path.exists(p):
            xlsx_path = p; break
    
    if not xlsx_path:
        print("ERROR: Excel fajl nije pronadjen!")
        print("Kopiraj fajl na server ili uploaduj ga.")
        sys.exit(1)
    
    print(f"Uvozim iz: {xlsx_path}")
    xl = pd.ExcelFile(xlsx_path)
    conn, db_type = get_conn()

    # Clear tables
    print("Brisanje starih podataka...")
    for tbl in ['kupci', 'cenovnik', 'dogadjaji', 'evidencija']:
        run_sql(conn, db_type, f"DELETE FROM {tbl}")
    conn.commit()

    # Kupci
    if 'Kupci' in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name='Kupci')
        df.columns = [col.strip().upper() for col in df.columns]
        rows = []
        for _, row in df.iterrows():
            naziv = str(row.get('NAZIV', '')).strip()
            if not naziv or naziv == 'nan': continue
            pib = str(row.get('PIB', '')).replace('.0','').strip()
            mb  = str(row.get('MB', '')).replace('.0','').strip()
            jbkjs = str(row.get('JBKJS', '')).split('.')[0].strip()
            adresa = str(row.get('ADRESA','')).strip()
            mesto = str(row.get('MESTO','')).strip()
            for v in ('nan','None','NaN'):
                if pib==v: pib=''
                if mb==v: mb=''
                if jbkjs==v: jbkjs=''
                if adresa==v: adresa=''
                if mesto==v: mesto=''
            rows.append((naziv, pib, mb, adresa, mesto, jbkjs))
        run_sql(conn, db_type, "INSERT INTO kupci (naziv, pib, mb, adresa, mesto, jbkjs) VALUES (?,?,?,?,?,?)", rows, many=True)
        conn.commit()
        print(f"Kupci: {len(rows)} uvezeno")

    # Cenovnik
    if 'Cenovnik' in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name='Cenovnik')
        df.columns = [col.strip().upper() for col in df.columns]
        rows = []
        for _, row in df.iterrows():
            naziv = str(row.get('NAZIV', '')).strip()
            if not naziv or naziv == 'nan': continue
            try:
                cena = float(str(row.get('CENA',0)).replace(',','.'))
                pdv = int(float(str(row.get('PDV',20))))
                status = str(row.get('STATUS','AKTIVNA')).strip()
                if status == 'nan': status = 'AKTIVNA'
                spec = str(row.get('SPECIFIKACIJA','')).strip()
                if spec == 'nan': spec = ''
                rows.append((naziv, cena, pdv, status, spec))
            except: pass
        run_sql(conn, db_type, "INSERT INTO cenovnik (naziv, cena, pdv, status, specifikacija) VALUES (?,?,?,?,?)", rows, many=True)
        conn.commit()
        print(f"Cenovnik: {len(rows)} uvezeno")

    # Dogadjaji
    if 'Opis' in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name='Opis')
        df.columns = [col.strip().upper() for col in df.columns]
        rows = []
        for _, row in df.iterrows():
            naziv = str(row.get('DOGADJAJ', '')).strip()
            if not naziv or naziv == 'nan': continue
            datum = str(row.get('DATUM', '')).strip()
            if datum == 'nan': datum = ''
            status = str(row.get('STATUS', 'AKTIVNA')).strip()
            if status == 'nan': status = 'AKTIVNA'
            rows.append((naziv, datum, status))
        run_sql(conn, db_type, "INSERT INTO dogadjaji (naziv, datum, status) VALUES (?,?,?)", rows, many=True)
        conn.commit()
        print(f"Dogadjaji: {len(rows)} uvezeno")

    # Evidencija
    if 'Evidencija' in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name='Evidencija')
        df.columns = [col.strip().upper() for col in df.columns]
        rows = []
        for _, row in df.iterrows():
            broj = str(row.get('BROJ', '')).strip()
            if not broj or broj == 'nan': continue
            def sv(col, default=''):
                val = row.get(col, default)
                try:
                    if pd.isna(val): return default
                except: pass
                s = str(val).strip()
                return default if s in ('nan','None','NaN') else s
            def fv(col):
                try: return float(row.get(col, 0))
                except: return 0.0
            stavke_txt = sv('STAVKE')
            import re
            stavke_list = []
            m = re.match(r'^(.+?)\s+x(\d+)\s+@\s+([\d.]+)$', stavke_txt)
            if m:
                stavke_list = [{"naziv": m.group(1).strip(), "kolicina": int(m.group(2)), "cena": float(m.group(3)), "pdv": 20}]
            else:
                stavke_list = [{"naziv": stavke_txt, "kolicina": 1, "cena": fv('OSNOV'), "pdv": 20}]
            stavke_json = json.dumps(stavke_list, ensure_ascii=False)
            try:
                dog_id = int(float(sv('DOGADJAJ_ID','0') or '0'))
            except: dog_id = None
            rows.append((broj, sv('DATUM_IZD'), sv('DATUM_VAL'),
                        sv('KUPAC_NAZIV'), sv('KUPAC_PIB').replace('.0',''),
                        str(int(float(sv('KUPAC_JBKJS','0') or '0'))) if sv('KUPAC_JBKJS') else '',
                        dog_id if dog_id else None, sv('DOGADJAJ_NAZIV'),
                        fv('OSNOV'), fv('PDV'), fv('UKUPNO'),
                        sv('STATUS','ČEKA'), sv('NAPOMENA'), stavke_json, 'Import'))
        run_sql(conn, db_type, 
            "INSERT INTO evidencija (broj, datum_izd, datum_val, kupac_naziv, kupac_pib, kupac_jbkjs, dogadjaj_id, dogadjaj_naziv, osnov, pdv, ukupno, status, napomena, stavke, korisnik_ime) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            rows, many=True)
        conn.commit()
        print(f"Evidencija: {len(rows)} uvezeno")

    conn.close()
    print("\nUvoz završen!")

if __name__ == '__main__':
    main()
