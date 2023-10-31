@echo off
call D:\ProgramData\miniconda3\Scripts\activate.bat
python D:\VeriDevOps\earlytool\display.py -u 192.168.0.101:9400

echo.
echo Press any key to exit...
pause > nul
exit /b