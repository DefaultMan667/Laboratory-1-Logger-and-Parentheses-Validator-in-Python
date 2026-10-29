@echo off
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
    python -B try_it.py
) else (
    py -3 -B try_it.py
)
if errorlevel 1 echo The program could not run. Check that Python 3 is installed.
echo.
echo Press any key to close this window.
pause >nul
