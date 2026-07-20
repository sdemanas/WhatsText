@echo off
REM Double-click this file to run WhatsText. No install, no terminal typing.
cd /d "%~dp0"
set PYTHONPATH=%~dp0src;%PYTHONPATH%

where python >nul 2>nul
if %errorlevel%==0 (
    python -m whatstext
    goto :end
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m whatstext
    goto :end
)

echo Python 3 wasn't found on this PC.
echo Install it from https://www.python.org/downloads/ then double-click this file again.

:end
pause
