@echo off
call C:\ProgramData\miniconda3\Scripts\activate.bat
python C:\Users\early\Desktop\codes\earlytool\monitor.py -i Ethernet

echo.
echo Press any key to exit...
pause > nul
exit /b