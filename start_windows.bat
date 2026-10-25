@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Installera beroendena enligt README forst.
 exit /b 1
)
.venv\Scripts\python.exe main.py
