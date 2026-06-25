# -*- coding: utf-8 -*-
import os, json, hashlib

DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_conn():
    if DATABASE_URL:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn, 'pg'
    else:
        import sqlite3
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'cmn.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        return conn, 'sqlite'

def init_db():
    conn, db_type = get_conn()
    c = conn.cursor()

    if db_type == 'pg':
        # PostgreSQL
        c.execute('''CREATE TABLE IF NOT EXISTS korisnici (
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            aktivan INTEGER DEFAULT 1,
            admin INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS kupci (
            id SERIAL PRIMARY KEY,
            naziv TEXT NOT NULL,
            pib TEXT,
            mb TEXT,
            adresa TEXT,
            mesto TEXT,
            jbkjs TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS cenovnik (
            id SERIAL PRIMARY KEY,
            naziv TEXT NOT NULL,
            cena REAL,
            pdv INTEGER DEFAULT 20,
            status TEXT DEFAULT 'AKTIVNA',
            specifikacija TEXT DEFAULT ''
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS dogadjaji (
            id SERIAL PRIMARY KEY,
            naziv TEXT NOT NULL,
            datum TEXT,
            status TEXT DEFAULT 'AKTIVNA',
            specifikacija TEXT DEFAULT ''
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS evidencija (
            id SERIAL PRIMARY KEY,
            broj TEXT NOT NULL,
            datum_izd TEXT,
            datum_val TEXT,
            kupac_naziv TEXT,
            kupac_pib TEXT,
            kupac_mb TEXT,
            kupac_adresa TEXT,
            kupac_mesto TEXT,
            kupac_jbkjs TEXT,
            kupac_extra TEXT DEFAULT '',
            dogadjaj_id INTEGER,
            dogadjaj_naziv TEXT,
            osnov REAL,
            pdv REAL,
            ukupno REAL,
            status TEXT DEFAULT 'ČEKA',
            napomena TEXT DEFAULT '',
            napomena_predracun TEXT DEFAULT '',
            specifikacija TEXT DEFAULT '',
            stavke TEXT,
            korisnik_id INTEGER,
            korisnik_ime TEXT,
            datum_kreiranja TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            storno INTEGER DEFAULT 0
        )''')
    else:
        # SQLite
        c.execute('''CREATE TABLE IF NOT EXISTS korisnici (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ime TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            aktivan INTEGER DEFAULT 1,
            admin INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS kupci (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT NOT NULL,
            pib TEXT, mb TEXT, adresa TEXT, mesto TEXT, jbkjs TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS cenovnik (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT NOT NULL,
            cena REAL, pdv INTEGER DEFAULT 20,
            status TEXT DEFAULT 'AKTIVNA',
            specifikacija TEXT DEFAULT ''
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS dogadjaji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT NOT NULL, datum TEXT,
            status TEXT DEFAULT 'AKTIVNA',
            specifikacija TEXT DEFAULT ''
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS evidencija (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broj TEXT NOT NULL,
            datum_izd TEXT, datum_val TEXT,
            kupac_naziv TEXT, kupac_pib TEXT, kupac_mb TEXT,
            kupac_adresa TEXT, kupac_mesto TEXT, kupac_jbkjs TEXT,
            kupac_extra TEXT DEFAULT '',
            dogadjaj_id INTEGER, dogadjaj_naziv TEXT,
            osnov REAL, pdv REAL, ukupno REAL,
            status TEXT DEFAULT 'ČEKA',
            napomena TEXT DEFAULT '',
            napomena_predracun TEXT DEFAULT '',
            specifikacija TEXT DEFAULT '',
            stavke TEXT,
            korisnik_id INTEGER, korisnik_ime TEXT,
            datum_kreiranja TEXT DEFAULT CURRENT_TIMESTAMP,
            storno INTEGER DEFAULT 0
        )''')

    conn.commit()

    # Default admin
    if db_type == 'pg':
        c.execute("SELECT COUNT(*) FROM korisnici")
        count = c.fetchone()[0]
    else:
        c.execute("SELECT COUNT(*) FROM korisnici")
        count = c.fetchone()[0]

    if count == 0:
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO korisnici (ime, username, password_hash, admin) VALUES (%s,%s,%s,%s)" if db_type=='pg' else
                  "INSERT INTO korisnici (ime, username, password_hash, admin) VALUES (?,?,?,?)",
                  ("Administrator", "admin", pw, 1))
        conn.commit()
        print("Kreiran admin korisnik: admin / admin123")

    conn.close()
    print(f"Baza inicijalizovana ({db_type})")

if __name__ == '__main__':
    init_db()
