@echo off
title VoiceMed Open Backend Server
cd /d "%~dp0"

echo ========================================================
echo   Starting VoiceMed Open Backend Server
echo ========================================================
echo.

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo Starting Uvicorn FastAPI Server on http://localhost:8000 ...
start /b uvicorn server:app --reload --host 0.0.0.0 --port 8000

echo Waiting 3 seconds for server startup...
timeout /t 3 /nobreak >nul

echo Running Test Client...
python test_client.py
pause