@echo off
call D:\ProgramData\Miniconda3\Scripts\activate.bat
python D:\VeriDevOps\earlytool\display.py -u localhost:9400

echo.
echo Press any key to exit...
pause > nul
exit /b