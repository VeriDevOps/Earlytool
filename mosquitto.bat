@echo off
call D:\ProgramData\Miniconda3\Scripts\activate.bat
"C:\Program Files\mosquitto\mosquitto.exe" -c "C:\Program Files\mosquitto\mosquitto.conf"

echo.
echo Press any key to exit...
pause > nul
exit /b