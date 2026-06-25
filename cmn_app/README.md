# CMN Predračun Manager — Web Aplikacija

## Sadržaj
```
cmn_app/
├── app.py              ← Flask aplikacija (glavni server)
├── pdf_gen.py          ← PDF generator (identičan originalu)
├── init_db.py          ← Inicijalizacija baze + uvoz Excel podataka
├── requirements.txt    ← Python paketi
├── Procfile            ← Za Render.com hosting
├── render.yaml         ← Konfiguracija za Render.com
├── instance/
│   └── cmn.db          ← SQLite baza (kreira se automatski)
├── static/
│   ├── img/            ← logo.png, pecat.png
│   └── fonts/          ← DejaVuSans fontovi
└── templates/          ← HTML stranice
```

## 🚀 Hosting na Render.com (Besplatno, pristup svuda)

### Korak 1: GitHub
1. Kreiraj GitHub nalog na https://github.com (ako nemaš)
2. Napravi novi repozitorijum (Repository) — nazovi ga `cmn-predracun`
3. Postavi sve fajlove iz ovog foldera na GitHub

### Korak 2: Render.com
1. Idi na https://render.com i registruj se (besplatno)
2. Klikni **"New +"** → **"Web Service"**
3. Poveži sa GitHub nalogom i izaberi `cmn-predracun` repozitorijum
4. Render automatski detektuje postavke iz `render.yaml`
5. Klikni **"Create Web Service"**
6. Čekaj 3-5 minuta — aplikacija je dostupna na `https://cmn-predracun.onrender.com`

### Korak 3: Baza podataka
- Baza se automatski kreira pri prvom pokretanju
- Svi uvezeni podaci (kupci, cenovnik, evidencija) su već tu
- Render čuva bazu između restartova zahvaljujući `disk` konfiguraciji

## 👤 Prijava
- **Korisničko ime:** `admin`  
- **Lozinka:** `admin123`  
⚠️ Odmah promeniti lozinku pri prvoj prijavi!

## 💾 Lokalno pokretanje (sa USB-a ili PC-a)

### Instalacija (jednom)
```bash
pip install -r requirements.txt
python init_db.py
```

### Pokretanje
```bash
python app.py
```
Otvori browser: http://localhost:5000

### Windows batch fajl (dupleklik za pokretanje)
```batch
@echo off
cd /d "%~dp0"
python app.py
```
Sačuvaj kao `pokreni.bat` — radi sa USB-a ako je Python instaliran.

## 📦 Backup baze
Baza je u `instance/cmn.db` — kopiraj ovaj fajl za backup.
Možeš ga uploadovati na Google Drive ručno ili automatski skriptom.

## 🔧 Dodavanje korisnika
Prijavi se kao admin → **Korisnici** → **Novi korisnik**

## ⚡ Razlike vs Desktop aplikacija
| Desktop | Web |
|---|---|
| Samo 1 korisnik | 2-5 simultanih korisnika |
| Excel baza | SQLite baza (brže) |
| Lokalni PDF fajlovi | Download u browseru |
| Windows only | Radi na svim uređajima |
