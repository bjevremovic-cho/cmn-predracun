@echo off
title CMN Predracun Manager
cd /d "%~dp0"
echo.
echo  ====================================
echo   CMN Predracun Manager - Pokretanje
echo  ====================================
echo.

:: Pronadji Python - pokusaj py, python, python3
set PYTHON=
where py >nul 2>&1 && set PYTHON=py
if "%PYTHON%"=="" where python >nul 2>&1 && set PYTHON=python
if "%PYTHON%"=="" where python3 >nul 2>&1 && set PYTHON=python3

if "%PYTHON%"=="" (
    echo.
    echo  GRESKA: Python nije pronadjen!
    echo.
    echo  Molimo instalirajte Python:
    echo  1. Idite na https://www.python.org/downloads/
    echo  2. Preuzmite Python 3.x
    echo  3. OBAVEZNO oznacite "Add Python to PATH"
    echo  4. Ponovo pokrenite pokreni.bat
    echo.
    pause
    exit /b 1
)

echo  Koristim: %PYTHON%
echo.

:: Pronadji pip
set PIP=
where pip >nul 2>&1 && set PIP=pip
if "%PIP%"=="" %PYTHON% -m pip --version >nul 2>&1 && set PIP=%PYTHON% -m pip

if "%PIP%"=="" (
    echo  Instalacija pip-a...
    %PYTHON% -m ensurepip --upgrade
    set PIP=%PYTHON% -m pip
)

:: Provjeri da li je flask instaliran
%PYTHON% -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo  Instalacija potrebnih paketa, sacekajte...
    echo.
    %PIP% install flask fpdf2 pandas openpyxl --quiet --no-warn-script-location
    if errorlevel 1 (
        echo.
        echo  GRESKA pri instalaciji paketa!
        echo  Pokusajte rucno: %PIP% install flask fpdf2 pandas openpyxl
        pause
        exit /b 1
    )
    echo  Paketi instalirani uspesno!
    echo.
)

:: Inicijalizuj bazu ako ne postoji
if not exist "instance\cmn.db" (
    echo  Inicijalizacija baze podataka...
    %PYTHON% init_db.py
    echo.
)

:: Otvori browser
echo  Otvaranje browsera...
start "" "http://localhost:5000"

echo.
echo  Aplikacija radi na: http://localhost:5000
echo  Login: admin / admin123
echo  Pritisnite Ctrl+C za zaustavljanje
echo.

%PYTHON% app.py
pause
