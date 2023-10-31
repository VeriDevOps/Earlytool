@echo off
call D:\ProgramData\miniconda3\Scripts\activate.bat
python D:\VeriDevOps\earlytool\monitor.py -i Ethernet -c trained_cicids17  -b "(tcp or udp) and src host 192.168.0.101"


echo.
echo Press any key to exit...
pause > nul
exit /b