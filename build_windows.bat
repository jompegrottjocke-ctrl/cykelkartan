@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -3.12 -m venv .venv
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --additional-hooks-dir packaging\hooks --name CykelframjandetMalmo --icon assets\icons\cykel.ico --add-data "assets;assets" --add-data "app\maps;app\maps" --collect-all osmnx --collect-all osmium main.py
if errorlevel 1 exit /b 1
echo Klar: dist\CykelframjandetMalmo\CykelframjandetMalmo.exe
