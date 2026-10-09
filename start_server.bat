@echo off
title VoiceMed Backend Server
cd /d "%~dp0"

echo ========================================================
echo   Starting VoiceMed Backend Server
echo ========================================================
echo.

set "PYTHON=python"
where python >nul 2>nul
if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo Python was not found. Install Python 3.10 or newer and add it to PATH.
        pause
        exit /b 1
    )
    set "PYTHON=py -3"
)

%PYTHON% -c "import fastapi, uvicorn" >nul 2>nul
if errorlevel 1 (
    echo Required packages are missing. Installing them for the current user...
    %PYTHON% -m pip install --user -r requirements.txt
    if errorlevel 1 (
        echo Dependency installation failed. Check your Python and pip installation.
        pause
        exit /b 1
    )
)

echo Starting Uvicorn FastAPI Server on http://localhost:8000 ...
start "VoiceMed Backend" /b %PYTHON% -m uvicorn server:app --reload --host 127.0.0.1 --port 8000

echo Waiting 3 seconds for server startup...
timeout /t 3 /nobreak >nul

echo Running Test Client...
%PYTHON% test_client.py
pause