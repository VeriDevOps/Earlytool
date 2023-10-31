@echo off
call C:\ProgramData\miniconda3\Scripts\activate.bat
python C:\Users\early\Desktop\codes\earlytool\monitor.py -i Ethernet -c trained_mqttset -b "(tcp or udp) and src host 10.0.2.4"

echo.
echo Press any key to exit...
pause > nul
exit /b