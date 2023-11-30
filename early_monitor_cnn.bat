@echo off
call D:\ProgramData\Miniconda3\Scripts\activate.bat
python D:\VeriDevOps\earlytool\monitor.py -i Ethernet -c trained_cicids17  -b "(tcp or udp) and src host 127.0.0.1"


echo.
echo Press any key to exit...
pause > nul
exit /b