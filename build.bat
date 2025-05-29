@echo off
echo Otel Rezervasyon Sistemi Setup Olusturuluyor...

REM Sanal ortamı aktif et
call venv\Scripts\activate

REM Gerekli paketleri yükle
pip install -r requirements.txt

REM PyInstaller ile exe oluştur
pyinstaller otel_rezervasyon.spec --clean

echo Setup olusturma tamamlandi.
echo Exe dosyasi: dist\OtelRezervasyon.exe

pause 