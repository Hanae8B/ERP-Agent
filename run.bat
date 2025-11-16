@echo off
REM ============================================================
REM Run ERP Agent GUI
REM ============================================================

REM Change directory to project folder
cd /d "C:\ERP Agent"

REM Run the GUI using full Python path
"C:\Python313\python.exe" gui.py

REM Pause so the console window stays open after execution
echo.
echo === Press any key to exit ===
pause
