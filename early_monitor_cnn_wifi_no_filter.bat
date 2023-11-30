@echo off
call D:\ProgramData\Miniconda3\Scripts\activate.bat
python D:\VeriDevOps\earlytool\monitor.py -i WLAN -c trained_cicids17


echo.
echo Press any key to exit...
pause > nul
exit /b