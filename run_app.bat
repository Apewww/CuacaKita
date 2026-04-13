@echo off
:: Pindah ke direktori aplikasi
cd /d "%~dp0"

:: Jalankan server menggunakan python
:: Pastikan python ada di PATH atau ganti dengan path absolut ke python.exe
python serve.py
pause
