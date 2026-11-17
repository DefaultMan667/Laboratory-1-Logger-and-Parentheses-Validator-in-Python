@echo off
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
    python -B shop.py
) else (
    py -3 -B shop.py
)
if errorlevel 1 echo The program could not run. Check that Python 3 is installed.
echo.
echo Press any key to close this window.
pause >nul
